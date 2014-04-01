# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging
import os
import random
import Queue
import string
import threading
import time

from xivo_cti import asterisk_ami_definitions as ami_def
from xivo_cti.ami import ami_callback_handler
from xivo_cti.ami import ami_logger
from xivo_cti.ami import ami_event_complete_logger
from xivo_cti.ami import ami_status_request_logger
from xivo_cti.ami.ami_response_handler import AMIResponseHandler
from xivo_cti.ami.initializer import AMIInitializer
from xivo_cti.ami.ami_callback_handler import AMICallbackHandler
from xivo_cti.ami.ami_agent_login_logoff import AMIAgentLoginLogoff
from xivo_cti.ioc.context import context
from xivo_cti import dao

logger = logging.getLogger('interface_ami')


class AMI(object):

    kind = 'AMI'
    LINE_SEPARATOR = '\r\n'
    EVENT_SEPARATOR = '\r\n\r\n'
    FIELD_SEPARATOR = ': '
    ALPHANUMS = string.uppercase + string.lowercase + string.digits

    def __init__(self, cti_server, innerdata, ami_class):
        self._ctiserver = cti_server
        self.innerdata = innerdata
        self.amiclass = ami_class
        self._input_buffer = ''
        self.waiting_actionid = {}
        self.actionids = {}
        self.originate_actionids = {}

    def init_connection(self):
        self.timeout_queue = Queue.Queue()
        ami_logger.AMILogger.register_callbacks()
        ami_event_complete_logger.AMIEventCompleteLogger.register_callbacks()
        ami_status_request_logger.AMIStatusRequestLogger.register_callbacks()
        AMIAgentLoginLogoff.register_callbacks()
        ami_agent_login_logoff = AMIAgentLoginLogoff.get_instance()
        ami_agent_login_logoff.queue_statistics_producer = self._ctiserver._queue_statistics_producer
        ami_agent_login_logoff.innerdata_dao = dao.innerdata
        self._ami_initializer = AMIInitializer()
        self._ami_initializer._ami_class = self.amiclass
        self._ami_initializer._ami_callback_handler = AMICallbackHandler.get_instance()

    def connect(self):
        logger.info('connecting ami .....')
        try:
            self._ami_initializer.register()
            self.amiclass.connect()
            self.amiclass.login()
            return self.amiclass.sock
        except Exception:
            logger.warning('unable to connect/login')

    def disconnect(self):
        logger.info('ami disconnected')
        self.amiclass.sock.close()

    def connected(self):
        if self.amiclass and self.amiclass.sock:
            try:
                return self.amiclass.sock.getpeername()
            except Exception:
                return None

    def cb_timer(self, *args):
        try:
            self.timeout_queue.put(args)
            os.write(self._ctiserver.pipe_queued_threads[1], 'ami:%s\n' %
                     self._ctiserver.myipbxid)
        except Exception:
            logger.exception('cb_timer %s', args)

    def checkqueue(self):
        ncount = 0
        while self.timeout_queue.qsize() > 0:
            ncount += 1
            (toload,) = self.timeout_queue.get()
            action = toload.get('action')
            if action == 'commandrequest':
                actionid = toload.get('properties')
                if actionid in self.waiting_actionid:
                    sockparams = self.waiting_actionid.get(actionid)
                    sockparams.makereply_close(actionid, 'timeout')
                    del self.waiting_actionid[actionid]
        return ncount

    def delayed_action(self, usefulmsg, replyto=None):
        actionid = self.make_actionid()
        self.amiclass.sendcommand('Command', [('Command', usefulmsg),
                                              ('ActionID', actionid)])
        if replyto is not None:
            self.waiting_actionid[actionid] = replyto
            replyto.replytimer = threading.Timer(2, self.cb_timer,
                                                 ({'action': 'commandrequest',
                                                   'properties': actionid},))
            replyto.replytimer.setName('Thread-ami-%s' % actionid)
            replyto.replytimer.start()

    def decode_raw_event(self, raw_event):
        return raw_event.decode('utf8', 'replace')

    def handle_event(self, input_data):
        """
        Handles the AMI events occuring on Asterisk.
        If the Event field is there, calls the handle_ami_function() function.
        """
        full_idata = self._input_buffer + input_data
        events = full_idata.split(self.EVENT_SEPARATOR)
        self._input_buffer = events.pop()

        for raw_event in events:
            decoded_event = self.decode_raw_event(raw_event)
            event = {}
            nocolon = []
            for line in decoded_event.split(self.LINE_SEPARATOR):
                if '\n' not in line:
                    if line != '--END COMMAND--':  # occurs when requesting "module reload xxx.so"
                        key_value = line.split(self.FIELD_SEPARATOR, 1)
                        if len(key_value) == 2:
                            key, value = key_value
                            event[key.strip()] = value
                        elif line.startswith('Asterisk Call Manager'):
                            logger.info('%s', line)
                else:
                    nocolon.append(line)

            if 'Event' in event and event['Event'] is not None:
                event_name = event['Event']
                for ik, interface in self._ctiserver.fdlist_established.iteritems():
                    if not isinstance(interface, str) and interface.kind == 'INFO' and interface.dumpami_enable:
                        if interface.dumpami_enable == ['all'] or event_name in interface.dumpami_enable:
                            doallow = True
                            if interface.dumpami_disable and event_name in interface.dumpami_disable:
                                doallow = False
                            if doallow:
                                ik.sendall('%.3f %s %s %s\n' %
                                           (time.time(),
                                            self._ctiserver.myipbxid,
                                            event_name,
                                            event))
                self.handle_ami_function(event_name, event)
            elif 'Response' in event and event['Response'] is not None:
                AMIResponseHandler.get_instance().handle_response(event)
                response = event['Response']
                if (response == 'Follows' and 'Privilege' in event
                        and event['Privilege'] == 'Command'):
                    reply = []
                    try:
                        for line in nocolon:
                            to_ignore = ('', '--END COMMAND--')
                            args = [a for a in line.split('\n') if a not in to_ignore]
                            reply.extend(args)

                        if 'ActionID' in event:
                            actionid = event['ActionID']
                            if actionid in self.waiting_actionid:
                                connreply = self.waiting_actionid[actionid]
                                if connreply is not None:
                                    connreply.replytimer.cancel()
                                    connreply.makereply_close(actionid, 'OK', reply)
                                del self.waiting_actionid[actionid]

                    except Exception:
                        logger.exception('(command reply)')
                    try:
                        self.amiresponse_follows(event)
                    except Exception:
                        logger.exception('response_follows (%s) (%s)', event, nocolon)

                elif response == 'Success':
                    try:
                        self.amiresponse_success(event)
                    except Exception:
                        logger.exception('response_success (%s) (%s)', event, nocolon)

                elif response == 'Error':
                    if 'ActionID' in event:
                        actionid = event['ActionID']
                        if actionid in self.waiting_actionid:
                            connreply = self.waiting_actionid.get(actionid)
                            if connreply is not None:
                                connreply.replytimer.cancel()
                                connreply.makereply_close(actionid, 'KO')
                            del self.waiting_actionid[actionid]
                    try:
                        self.amiresponse_error(event)
                    except Exception:
                        logger.exception('response_error (%s) (%s)', event, nocolon)

    def handle_ami_function(self, evfunction, event):
        """
        Handles the AMI events related to a given function (i.e. containing the Event field).
        It roughly only dispatches them to the relevant commandset's methods.
        """
        ami_18 = context.get('ami_18')
        functions = []
        if 'Event' in event:
            functions.extend(ami_callback_handler.AMICallbackHandler.get_instance().get_callbacks(event))
        if evfunction in ami_def.evfunction_to_method_name:
            methodname = ami_def.evfunction_to_method_name.get(evfunction)
            if hasattr(ami_18, methodname):
                functions.append(getattr(ami_18, methodname))

        self._run_functions_with_event(functions, event)

    def amiresponse_success(self, event):
        actionid = event.get('ActionID')
        if actionid and actionid in self.actionids:
            properties = self.actionids.pop(actionid)
            mode = properties['mode']
            if mode == 'newchannel':
                self._handle_newchannel_success(event, properties)
            elif mode == 'useraction':
                self._handle_useraction_success(event, actionid, properties, mode)
            elif mode == 'extension':
                self._handle_extension_success(event, actionid, properties, mode)
            elif mode == 'vmupdate':
                self._handle_vmupdate_success(event, properties)

    def amiresponse_error(self, event):
        actionid = event.get('ActionID')
        if actionid and actionid in self.actionids:
            properties = self.actionids.pop(actionid)
            mode = properties['mode']
            logger.warning('amiresponse_error %s %s : %s - %s',
                           actionid, mode, event, properties)
            if mode == 'useraction':
                request = properties.get('request')
                cn = request.get('requester')
                cn.reply({'class': 'ipbxcommand',
                          'response': 'ko',
                          'command': request.get('ipbxcommand'),
                          'replyid': request.get('commandid')})

    def amiresponse_follows(self, event):
        actionid = event.get('ActionID')
        if actionid and actionid in self.actionids:
            properties = self.actionids.pop(actionid)
            mode = properties['mode']
            logger.info('amiresponse_follows %s %s : %s - %s',
                        actionid, mode, event, properties)

    def execute_and_track(self, actionid, params):
        conn_ami = self.amiclass
        mode = params.get('mode')
        if conn_ami and 'amicommand' in params:
            amicommand = params['amicommand']
            if hasattr(conn_ami, amicommand):
                conn_ami.actionid = actionid
                self.actionids[actionid] = params
                amiargs = params.get('amiargs')
                return getattr(conn_ami, amicommand)(* amiargs)
            else:
                logger.warning('mode %s : no such AMI command %s',
                               mode, amicommand)
                return 'unknown'
        else:
            logger.warning('mode %s : no AMI connection', mode)
            return 'noconn'

    def _handle_newchannel_success(self, event, properties):
        if 'Value' in event and event['Value']:
            value = event['Value']
            channel, dummyvarname = properties.get('amiargs')
            if value in self.originate_actionids:
                request = self.originate_actionids[value].get('request')
                cn = request.get('requester')
                cn.reply({'class': 'ipbxcommand',
                          'autocall_channel': channel,
                          'command': request.get('ipbxcommand'),
                          'replyid': request.get('commandid')})

    def _handle_extension_success(self, event, actionid, properties, mode):
        ami_18 = context.get('ami_18')
        msg = event.get('Message')
        if msg and msg == 'Extension Status':
            ami_18.amiresponse_extensionstatus(event)

    def _handle_vmupdate_success(self, event, properties):
        try:
            mailbox = event['Mailbox']
            self.innerdata.voicemailupdate(mailbox,
                                           event['NewMessages'],
                                           event['OldMessages'])
        except KeyError:
            logger.warning('Could not update voicemail info: %s', event)

    def _handle_useraction_success(self, event, actionid, properties, mode):
        request = properties.get('request')
        cn = request.get('requester')
        try:
            cn.reply({'class': 'ipbxcommand',
                      'response': 'ok',
                      'command': request.get('ipbxcommand'),
                      'replyid': request.get('commandid')})
        except Exception:
            # when requester is not connected any more ...
            pass

        if 'amicommand' in properties:
            if properties['amicommand'] in ['originate',
                                            'txfax']:
                self.originate_actionids[actionid] = properties
            elif ('mailboxcount' in properties['amicommand']
                  and 'amiargs' in properties
                  and len(properties['amiargs']) > 1):
                # The context is not part of this event, it's only part
                # of the request when using track_and_execute with an
                # extra argument
                context = properties['amiargs'][1]
                fullmailbox = event['Mailbox']
                self.innerdata.voicemailupdate(fullmailbox,
                                               event['NewMessages'],
                                               event['OldMessages'])

    def _run_functions_with_event(self, functions, event):
        for function in functions:
            try:
                function(event)
            except Exception:
                logger.exception('Exception caught in callback list for event: %s', event)

    @classmethod
    def make_actionid(cls):
        return ''.join(random.sample(cls.ALPHANUMS, 10))
