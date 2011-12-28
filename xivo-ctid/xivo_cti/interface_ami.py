# vim: set fileencoding=utf-8 :
# XiVO CTI Server

# Copyright (C) 2007-2011  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os
import random
import Queue
import string
import threading
import time

from xivo_cti import xivo_ami, cti_config
from xivo_cti import asterisk_ami_definitions as ami_def

ALPHANUMS = string.uppercase + string.lowercase + string.digits


class AMI:
    kind = 'AMI'
    LINE_SEPARATOR = '\r\n'
    EVENT_SEPARATOR = '\r\n\r\n'
    FIELD_SEPARATOR = ': '

    def __init__(self, ctiserver, ipbxid):
        self._ctiserver = ctiserver
        self.ipbxid = ipbxid
        self.innerdata = self._ctiserver.safe.get(self.ipbxid)
        self.log = logging.getLogger('interface_ami(%s)' % self.ipbxid)
        self._input_buffer = ''
        self.waiting_actionid = {}
        self.actionids = {}
        self.originate_actionids = {}
        config = cti_config.Config.get_instance()
        ipbxconfig = (config.getconfig('ipbxes').get(self.ipbxid)
                      .get('ipbx_connection'))
        self.ipaddress = ipbxconfig.get('ipaddress', '127.0.0.1')
        self.ipport = int(ipbxconfig.get('ipport', 5038))
        self.ami_login = ipbxconfig.get('username', 'xivouser')
        self.ami_pass = ipbxconfig.get('password', 'xivouser')
        self.timeout_queue = Queue.Queue()
        self.amicl = None

    def connect(self):
        try:
            self.amicl = xivo_ami.AMIClass(self.ipbxid,
                                           self.ipaddress, self.ipport,
                                           self.ami_login, self.ami_pass,
                                           True)
            self.amicl.connect()
            self.amicl.login()
            return self.amicl.sock
        except Exception:
            self.log.exception('unable to connect/login')

    def disconnect(self):
        self.amicl.sock.close()
        self.amicl = None

    def connected(self):
        if self.amicl and self.amicl.sock:
            try:
                return self.amicl.sock.getpeername()
            except Exception:
                return None

    def initrequest(self, phaseid):
        # 'CoreSettings', 'CoreStatus', 'ListCommands',
        for initrequest in ami_def.manager_commands.get('fetchstatuses'):
            actionid = 'init_%s:%s-%d' % (initrequest.lower(),
                                          phaseid,
                                          int(time.time()))
            params = {
                'mode': 'init',
                'amicommand': 'sendcommand',
                'amiargs': (initrequest.lower(), [])
                }
            self.execute_and_track(actionid, params)
        self.amicl.setactionid('init_close_%s' % phaseid)

    def cb_timer(self, *args):
        try:
            self.log.info('cb_timer (timer finished at %s) %s' %
                          (time.asctime(), args))
            self.timeout_queue.put(args)
            os.write(self._ctiserver.pipe_queued_threads[1], 'ami:%s\n' %
                      self.ipbxid)
        except Exception:
            self.log.exception('cb_timer %s' % args)

    def checkqueue(self):
        self.log.info('entering checkqueue')
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
                else:
                    self.log.warning('timeout on actionid %s but no more in our structure' % actionid)
        return ncount

    def delayed_action(self, usefulmsg, replyto):
        actionid = ''.join(random.sample(ALPHANUMS, 10))
        self.amicl.sendcommand('Command', [('Command', usefulmsg),
                                           ('ActionID', actionid)])
        self.waiting_actionid[actionid] = replyto
        replyto.replytimer = threading.Timer(2, self.cb_timer,
                                             ({'action': 'commandrequest',
                                               'properties': actionid},))
        replyto.replytimer.setName('Thread-ami-%s' % actionid)
        replyto.replytimer.start()

    def handle_event(self, input_data):
        """
        Handles the AMI events occuring on Asterisk.
        If the Event field is there, calls the handle_ami_function() function.
        """
        full_idata = self._input_buffer + input_data
        events = full_idata.split(self.EVENT_SEPARATOR)
        self._input_buffer = events.pop()

        for raw_event in events:
            try:
                decoded_event = raw_event.decode('utf8')
            except Exception:
                self.log.exception('could not decode event %r' % (raw_event))
                continue
            event = {}
            nocolon = []
            for line in decoded_event.split(self.LINE_SEPARATOR):
                if line.find('\n') < 0:
                    if line != '--END COMMAND--':  # occurs when requesting "module reload xxx.so"
                        key_value = line.split(self.FIELD_SEPARATOR, 1)
                        if len(key_value) == 2:
                            event[key_value[0]] = key_value[1]
                        elif line.startswith('Asterisk Call Manager'):
                            self.log.info('%s' % (line))
                else:
                    nocolon.append(line)

            if len(nocolon) > 1:
                self.log.warning('nocolon is %s' % (nocolon))

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
                                            self.ipbxid,
                                            event_name,
                                            event))
                self.handle_ami_function(event_name, event)

                if event_name not in ['Newexten',
                                      'Newchannel',
                                      'Newstate',
                                      'Newcallerid']:
                    pass
            else:
                if 'Response' in event and event['Response'] is not None:
                    response = event['Response']
                    if (response == 'Follows' and 'Privilege' in event
                            and event['Privilege'] == 'Command'):
                        reply = []
                        try:
                            for line in nocolon:
                                to_ignore = ('', '--END COMMAND--')
                                args = [a for a in line.split('\n') if a not in to_ignore]
                                reply.extend(args)
                                if len(args):
                                    self.log.info('Response : %s' % (args))

                            if 'ActionID' in event:
                                actionid = event['ActionID']
                                if actionid in self.waiting_actionid:
                                    connreply = self.waiting_actionid[actionid]
                                    if connreply is not None:
                                        connreply.replytimer.cancel()
                                        connreply.makereply_close(actionid, 'OK', reply)
                                    del self.waiting_actionid[actionid]

                        except Exception, e:
                            self.log.exception('(command reply)')
                            print e
                        try:
                            self.amiresponse_follows(event)
                        except Exception:
                            self.log.exception('response_follows (%s) (%s)' % (event, nocolon))

                    elif response == 'Success':
                        try:
                            self.amiresponse_success(event)
                        except Exception:
                            self.log.exception('response_success (%s) (%s)' % (event, nocolon))

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
                            self.log.exception('response_error (%s) (%s)' % (event, nocolon))
                    else:
                        self.log.warning('Response=%s (untracked) : %s' % (response, event))

                elif len(event) > 0:
                    self.log.warning('XXX: %s' % (event))
                else:
                    self.log.warning('Other : %s' % (event))
        event_count = len(events)
        if event_count > 200:
            self.log.info('handled %d (> 200) events' % (event_count))

    def handle_ami_function(self, evfunction, this_event):
        """
        Handles the AMI events related to a given function (i.e. containing the Event field).
        It roughly only dispatches them to the relevant commandset's methods.
        """
        try:
            if 'Privilege' in this_event:
                this_event.pop('Privilege')
            if (evfunction in ami_def.evfunction_to_method_name):
                methodname = ami_def.evfunction_to_method_name.get(evfunction)
                if hasattr(self._ctiserver.commandclass, methodname):
                    getattr(self._ctiserver.commandclass, methodname)(this_event)
                else:
                    self.log.warning('this event (%s) is tracked but no %s method is defined : %s'
                                     % (evfunction, methodname, this_event))
            else:
                self.log.warning('this event (%s) is not tracked : %s'
                                 % (evfunction, this_event))

        except Exception:
            self.log.exception('%s : event %s' % (evfunction, this_event))

    def amiresponse_success(self, event):
        if 'ActionID' in event:
            actionid = event.pop('ActionID')
        else:
            self.log.info('amiresponse_success (no ActionID) %s' % event)
            return

        if actionid in self.actionids:
            properties = self.actionids.pop(actionid)
            mode = properties.pop('mode')
            if mode == 'newchannel':
                value = event.pop('Value')
                if value:
                    # self.log.info('amiresponse_success %s %s : %s %s : %s'
                    # % (actionid, mode, value, properties, event))
                    (channel, dummyvarname) = properties.get('amiargs')
                    self.innerdata.autocall(channel, value)
                    # we tell the original requester of the ipbxcommand action
                    # about the channel he actually created
                    if value in self.originate_actionids:
                        request = self.originate_actionids[value].get('request')
                        cn = request.get('requester')
                        cn.reply({'class': 'ipbxcommand',
                                  'autocall_channel': channel,
                                  'command': request.get('ipbxcommand'),
                                  'replyid': request.get('commandid')})
            elif mode == 'useraction':
                self.log.info('amiresponse_success %s %s : %s - %s'
                              % (actionid, mode, event, properties))
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
                                                    'origapplication',
                                                    'txfax']:
                        self.originate_actionids[actionid] = properties
                    elif ('mailboxcount' in properties['amicommand']
                          and 'amiargs' in properties
                          and len(properties['amiargs']) > 1):
                        # The context is not part of this event, it's only part
                        # of the request when using track_and_execute with an
                        # extra argument
                        context = properties['amiargs'][1]
                        fullmailbox = event['Mailbox'] + '@' + context
                        self.innerdata.voicemailupdate(fullmailbox,
                                                       event['NewMessages'],
                                                       event['OldMessages'])
            elif mode == 'extension':
                msg = event.pop('Message')
                if msg == 'Extension Status':
                    self._ctiserver.commandclass.amiresponse_extensionstatus(event)
                else:
                    self.log.warning('amiresponse_success %s %s : %s - %s - unknown msg %s'
                                     % (actionid, mode, event, properties, msg))
            elif mode == 'init':
                self.log.info('amiresponse_success %s %s : %s'
                              % (actionid, mode, event))
            elif mode == 'presence':
                pass
            elif mode == 'vmupdate':
                try:
                    self.innerdata.voicemailupdate(
                        event['Mailbox'] + '@' + properties['amiargs'][1],
                        event['NewMessages'],
                        event['OldMessages'])
                except KeyError:
                    self.log.warning('Could not update voicemail info: %s', event)
            else:
                self.log.info('amiresponse_success %s %s (?) : %s'
                              % (actionid, mode, event))
        else:
            self.log.warning('amiresponse_success %s (no record) : %s'
                             % (actionid, event))
        return

    def amiresponse_error(self, event):
        if 'ActionID' in event:
            actionid = event.pop('ActionID')
        else:
            self.log.warning('amiresponse_error (no ActionID) %s' % event)
            return

        if actionid in self.actionids:
            properties = self.actionids.pop(actionid)
            mode = properties.pop('mode')
            self.log.warning('amiresponse_error %s %s : %s - %s'
                             % (actionid, mode, event, properties))
            if mode == 'useraction':
                request = properties.get('request')
                cn = request.get('requester')
                cn.reply({'class': 'ipbxcommand',
                          'response': 'ko',
                          'command': request.get('ipbxcommand'),
                          'replyid': request.get('commandid')})
        else:
            self.log.warning('amiresponse_error %s (no record) : %s'
                             % (actionid, event))
        return

    def amiresponse_follows(self, event):
        if 'ActionID' in event:
            actionid = event.pop('ActionID')
        else:
            self.log.warning('amiresponse_follows (no ActionID) %s' % event)
            return

        if actionid in self.actionids:
            properties = self.actionids.pop(actionid)
            mode = properties.pop('mode')
            self.log.info('amiresponse_follows %s %s : %s - %s'
                          % (actionid, mode, event, properties))
        else:
            self.log.warning('amiresponse_follows %s (no record) : %s'
                             % (actionid, event))

    def execute_and_track(self, actionid, params):
        conn_ami = self.amicl
        amicommand = params.get('amicommand')
        amiargs = params.get('amiargs')
        mode = params.get('mode')
        if conn_ami:
            if hasattr(conn_ami, amicommand):
                conn_ami.actionid = actionid
                self.actionids[actionid] = params
                ret = getattr(conn_ami, amicommand)(* amiargs)
            else:
                self.log.warning('mode %s : no such AMI command %s' % (mode, amicommand))
                ret = 'unknown'
        else:
            self.log.warning('mode %s : no AMI connection' % mode)
            ret = 'noconn'
        return ret
