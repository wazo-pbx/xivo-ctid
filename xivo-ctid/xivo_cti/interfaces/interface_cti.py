# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

import cjson
import logging
import time
import random

from xivo_cti import cti_command
from xivo_cti.cti_config import ALPHANUMS, CTI_PROTOCOL_VERSION
from xivo_cti.cti.cti_command_handler import CTICommandHandler
from xivo_cti.cti.commands.login_id import LoginID
from xivo_cti.cti.cti_command_runner import CTICommandRunner
from xivo_cti.interfaces import interfaces
from xivo_cti.ioc.context import context

logger = logging.getLogger('interface_cti')


class serialJson(object):

    def decode(self, linein):
        # Output of the cjson.decode is a Unicode object, even though the
        # non-ASCII characters have not been decoded.
        # Without the .decode('utf-8'), some Unicode character (try asian, not european)
        # will not be interpreted correctly.
        v = cjson.decode(linein.decode('utf-8').replace('\\/', '/'))
        return v

    def encode(self, obj):
        obj['timenow'] = time.time()
        return cjson.encode(obj)


class NotLoggedException(StandardError):
    pass


class CTI(interfaces.Interfaces):

    kind = 'CTI'
    sep = '\n'

    def __init__(self, ctiserver):
        interfaces.Interfaces.__init__(self, ctiserver)
        self.connection_details = {}
        self.serial = serialJson()
        self.transferconnection = {}
        self._cti_command_handler = CTICommandHandler(self)
        self._cti_command_runner = CTICommandRunner()
        self._register_login_callbacks()

    def connected(self, connid):
        interfaces.Interfaces.connected(self, connid)

    def user_id(self):
        try:
            user_id = self.connection_details['userid']
        except KeyError:
            raise NotLoggedException()
        else:
            return user_id

    def _register_login_callbacks(self):
        LoginID.register_callback_params(self.receive_login_id, ['userlogin',
                                                                 'xivo_version',
                                                                 'cti_connection'])

    def disconnected(self, cause):
        logger.info('disconnected %s', cause)
        self.logintimer.cancel()
        if self.transferconnection and self.transferconnection.get('direction') == 'c2s':
            logger.info('%s got the file ...', self.transferconnection.get('faxobj').fileid)
        else:
            try:
                user_service_manager = context.get('user_service_manager')
                user_id = self.user_id()
                if (cause == self.DisconnectCause.by_client
                    or cause == self.DisconnectCause.by_server_stop
                    or cause == self.DisconnectCause.by_server_reload
                    or cause == self.DisconnectCause.broken_pipe):
                    user_service_manager.disconnect_no_action(user_id)
                else:
                    raise TypeError('invalid DisconnectCause %s' % cause)
            except NotLoggedException:
                logger.warning('Called disconnected with no user_id')

    def manage_connection(self, msg):
        if not self.connection_details.get('authenticated', False) and 'login_':
            if 'class' in msg and 'login_' in msg:
                pass
            else:
                return 'error', {'closemenow': True,
                                 'error_string': 'Not authenticated'}
        if self.transferconnection:
            if self.transferconnection.get('direction') == 'c2s':
                faxobj = self.transferconnection.get('faxobj')
                self.logintimer.cancel()
                logger.info('%s transfer connection : %d received', faxobj.fileid, len(msg))
                faxobj.setbuffer(msg)
                faxobj.launchasyncs()
        else:
            multimsg = msg.split(self.sep)
            for usefulmsgpart in multimsg:
                cmd = self.serial.decode(usefulmsgpart)
                return self._run_functions(cmd)
        return []

    def _run_functions(self, decoded_command):
        replies = []

        # Commands from the CTICommandHandler
        self._cti_command_handler.parse_message(decoded_command)
        replies.extend(self._cti_command_handler.run_commands())

        # Commands from the cti_command.Command class
        if not replies:
            command = cti_command.Command(self, decoded_command)
            replies.extend(command.parse())

        return [reply for reply in replies if reply]

    def set_as_transfer(self, direction, faxobj):
        logger.info('%s set_as_transfer %s', faxobj.fileid, direction)
        self.transferconnection = {'direction': direction,
                                   'faxobj': faxobj}

    def append_msg(self, msg):
        if self.transferconnection:
            if self.transferconnection.get('direction') == 's2c':
                self.connid.append_queue(msg)
        else:
            self.connid.append_queue(self.serial.encode(msg) + '\n')

    def reply(self, msg):
        if self.transferconnection:
            if self.transferconnection.get('direction') == 's2c':
                self.connid.append_queue(msg)
                logger.info('transfer connection %d sent', len(msg))
        else:
            self.send_message(msg)

    def send_message(self, msg):
        self.connid.append_queue(self.serial.encode(msg) + '\n')

    def loginko(self, errorstring):
        logger.warning('user can not connect (%s) : sending %s',
                       self.connection_details, errorstring)
        # self.logintimer.cancel() + close
        tosend = {'class': 'loginko',
                  'error_string': errorstring}
        return self.serial.encode(tosend)

    def receive_login_id(self, login, version, connection):
        if connection != self:
            return []

        if version != CTI_PROTOCOL_VERSION:
            return 'error', {'error_string': 'xivoversion_client:%s;%s' % (version, CTI_PROTOCOL_VERSION),
                             'class': 'login_id'}

        innerdata = self._ctiserver.safe
        user_dict = innerdata.xod_config.get('users').finduser(login)

        if user_dict:
            self.connection_details.update({'ipbxid': self._ctiserver.myipbxid,
                                            'userid': str(user_dict.get('id'))})

        session_id = ''.join(random.sample(ALPHANUMS, 10))
        self.connection_details['prelogin'] = {'sessionid': session_id}

        return 'message', {'sessionid': session_id,
                           'class': 'login_id',
                           'xivoversion': version}


class CTIS(CTI):
    kind = 'CTIS'
