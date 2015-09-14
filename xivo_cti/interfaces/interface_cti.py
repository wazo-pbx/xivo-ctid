# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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
import random

from xivo_cti import cti_command
from xivo_cti import CTI_PROTOCOL_VERSION
from xivo_cti import ALPHANUMS
from xivo_cti.cti.cti_command_handler import CTICommandHandler
from xivo_cti.cti.commands.login_id import LoginID
from xivo_cti.interfaces import interfaces
from xivo_cti.ioc.context import context
from xivo_dao import user_dao

logger = logging.getLogger('interface_cti')


class NotLoggedException(StandardError):
    pass


class CTI(interfaces.Interfaces):

    kind = 'CTI'

    def __init__(self, ctiserver, cti_msg_decoder, cti_msg_encoder):
        interfaces.Interfaces.__init__(self, ctiserver)
        self._cti_msg_decoder = cti_msg_decoder
        self._cti_msg_encoder = cti_msg_encoder
        self.connection_details = {}
        self.transferconnection = {}
        self._cti_command_handler = CTICommandHandler(self)
        self._register_login_callbacks()

    def __str__(self):
        user_id = self.connection_details.get('userid', 'Not logged')
        return '<CTI connection to user {} at {}>'.format(user_id, id(self))

    def answer_cb(self):
        pass

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
        self.login_task.cancel()
        if self.transferconnection and self.transferconnection.get('direction') == 'c2s':
            logger.info('%s got the file ...', self.transferconnection.get('faxobj').fileid)
        else:
            self._remove_auth_token()
            try:
                user_service_manager = context.get('user_service_manager')
                user_id = self.user_id()
                if (cause == self.DisconnectCause.by_client or
                    cause == self.DisconnectCause.by_server_stop or
                    cause == self.DisconnectCause.by_server_reload or
                    cause == self.DisconnectCause.broken_pipe):
                    user_service_manager.disconnect_no_action(user_id)
                else:
                    raise TypeError('invalid DisconnectCause %s' % cause)
            except NotLoggedException:
                logger.warning('Called disconnected with no user_id')

    def _remove_auth_token(self):
        token = self.connection_details.get('auth_token')
        user_id = self.connection_details.get('userid')
        if token and user_id:
            self._ctiserver.safe.user_remove_auth_token(user_id, token)

    def manage_connection(self, msg):
        replies = []
        if self.transferconnection:
            if self.transferconnection.get('direction') == 'c2s':
                self.transferconnection['data'] += msg
                if msg.endswith('\n'):
                    data = self.transferconnection['data'][:-1]
                    faxobj = self.transferconnection['faxobj']
                    logger.info('%s transfer connection : %d received', faxobj.fileid, len(data))
                    faxobj.setbuffer(data)
                    faxobj.launchasyncs()
        else:
            commands = self._cti_msg_decoder.decode(msg)
            for command in commands:
                replies.extend(self._run_functions(command))
        return replies

    def _is_authenticated(self):
        return self.connection_details.get('authenticated', False)

    def _run_functions(self, decoded_command):
        if not self._is_authenticated() and not decoded_command['class'].startswith('login_'):
            return []
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
        self.login_task.cancel()
        self.transferconnection = {'direction': direction,
                                   'faxobj': faxobj,
                                   'data': ''}

    def reply(self, msg):
        if not self.transferconnection:
            self.connid.append_queue(self._cti_msg_encoder.encode(msg))

    def send_message(self, msg):
        if not self.transferconnection:
            self.connid.append_queue(self._cti_msg_encoder.encode(msg))

    def send_encoded_message(self, data):
        if not self.transferconnection:
            self.connid.append_queue(data)

    def receive_login_id(self, login, version, connection):
        if connection != self:
            return []

        if version != CTI_PROTOCOL_VERSION:
            return 'error', {'error_string': 'xivoversion_client:%s;%s' % (version, CTI_PROTOCOL_VERSION),
                             'class': 'login_id'}

        innerdata = self._ctiserver.safe
        user_dict = innerdata.xod_config.get('users').finduser(login)
        if not user_dict:
            return 'error', {
                'error_string': 'login_password',
                'class': 'login_id',
            }

        user_id = user_dict.get('id')

        if user_dict:
            self.connection_details.update({'ipbxid': self._ctiserver.myipbxid,
                                            'userid': str(user_id)})
            self.answer_cb = self._get_answer_cb(user_id)

        session_id = ''.join(random.sample(ALPHANUMS, 10))
        self.connection_details['prelogin'] = {'sessionid': session_id}

        return 'message', {'sessionid': session_id,
                           'class': 'login_id',
                           'xivoversion': version}

    def _get_answer_cb(self, user_id):
        device_manager = context.get('device_manager')
        try:
            device_id = user_dao.get_device_id(user_id)
            return device_manager.get_answer_fn(device_id)
        except LookupError:
            return self.answer_cb


class CTIS(CTI):
    kind = 'CTIS'
