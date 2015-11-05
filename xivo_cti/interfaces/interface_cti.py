# -*- coding: utf-8 -*-

# Copyright (C) 2007-2016 Avencall
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
from xivo_cti import config
from xivo_cti.cti.cti_command_handler import CTICommandHandler
from xivo_cti.cti.commands.login_id import LoginID
from xivo_cti.cti.commands.starttls import StartTLS
from xivo_cti.interfaces import interfaces
from xivo_cti.ioc.context import context
from xivo_cti.database import user_db

logger = logging.getLogger('interface_cti')


class NotLoggedException(StandardError):
    pass


class CTI(interfaces.Interfaces):

    kind = 'CTI'

    def __init__(self, ctiserver, cti_msg_decoder, cti_msg_encoder):
        interfaces.Interfaces.__init__(self, ctiserver)
        self._cti_msg_decoder = cti_msg_decoder
        self._cti_msg_encoder = cti_msg_encoder
        self.connection_details = {'ipbxid': ctiserver.myipbxid}
        self._cti_command_handler = CTICommandHandler(self)
        self._register_login_callbacks()
        self._starttls_sent = False
        self._starttls_status_received = False

    def connected(self, connid):
        logger.debug('connected: sending starttls')
        super(CTI, self).connected(connid)
        if config['main']['starttls'] and not self._starttls_sent:
            StartTLS.register_callback_params(self._on_starttls, ['status', 'cti_connection'])
            self.send_message({'class': 'starttls'})
            self._starttls_sent = True

    def _on_starttls(self, status, connection):
        if connection != self or self._starttls_status_received:
            return

        # TODO: add a StartTLS.deregister when it gets merged
        self.send_message({'class': 'starttls',
                           'starttls': status})
        self._starttls_status_received = True

        if status:
            task_queue = context.get('task_queue')
            task_queue.put(self.connid.upgrade_ssl)

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
        commands = self._cti_msg_decoder.decode(msg)
        for command in commands:
            replies.extend(self._run_functions(command))
        return replies

    def _is_authenticated(self):
        return self.connection_details.get('authenticated', False)

    def _run_functions(self, decoded_command):
        no_auth_commands = ['login_id', 'login_pass', 'login_capas', 'starttls']
        if not self._is_authenticated() and decoded_command['class'] not in no_auth_commands:
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

    def reply(self, msg):
        self.connid.append_queue(self._cti_msg_encoder.encode(msg))

    def send_message(self, msg):
        self.connid.append_queue(self._cti_msg_encoder.encode(msg))

    def send_encoded_message(self, data):
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
            self.connection_details['userid'] = str(user_id)
            self.answer_cb = self._get_answer_cb(user_id)

        session_id = ''.join(random.sample(ALPHANUMS, 10))
        self.connection_details['prelogin'] = {'sessionid': session_id}

        return 'message', {'sessionid': session_id,
                           'class': 'login_id',
                           'xivoversion': version}

    def _get_answer_cb(self, user_id):
        device_manager = context.get('device_manager')
        try:
            device_id = user_db.get_device_id(user_id)
            return device_manager.get_answer_fn(device_id)
        except LookupError:
            return self.answer_cb
