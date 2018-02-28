# -*- coding: utf-8 -*-
# Copyright (C) 2007-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from datetime import timedelta

from xivo_cti import cti_command
from xivo_cti import config
from xivo_cti.authentication import AuthenticationHandler
from xivo_cti.interfaces.interfaces import Interfaces, DisconnectCause
from xivo_cti.cti.cti_command_handler import CTICommandHandler
from xivo_cti.cti.commands.starttls import StartTLS
from xivo_cti.interfaces import interfaces
from xivo_cti.ioc.context import context
from xivo_cti.database import user_db

TWO_MONTHS = timedelta(days=60).total_seconds()

logger = logging.getLogger('interface_cti')


class NotLoggedException(StandardError):
    pass


class CTI(Interfaces):

    kind = 'CTI'

    def __init__(self, ctiserver, broadcast_cti_group, cti_msg_decoder, cti_msg_encoder):
        interfaces.Interfaces.__init__(self, ctiserver)
        self._cti_msg_decoder = cti_msg_decoder
        self._cti_msg_encoder = cti_msg_encoder
        self.connection_details = {'ipbxid': ctiserver.myipbxid}
        self._cti_command_handler = CTICommandHandler(self)
        self._starttls_sent = False
        self._starttls_status_received = False
        self._auth_client = None
        self._async_runner = context.get('async_runner')
        self._task_queue = context.get('task_queue')
        self._auth_handler = AuthenticationHandler(self, self._on_auth_success)
        self._broadcast_cti_group = broadcast_cti_group

    def connected(self, connid):
        logger.debug('connected: sending starttls')
        super(CTI, self).connected(connid)
        self._auth_handler.run()
        if config['main']['starttls'] and not self._starttls_sent:
            StartTLS.register_callback_params(self._on_starttls, ['status', 'cti_connection'])
            self.send_message({'class': 'starttls'})
            self._starttls_sent = True

    def _on_starttls(self, status, connection):
        if connection != self or self._starttls_status_received:
            return

        StartTLS.deregister_callback(self._on_starttls)
        self.send_message({'class': 'starttls',
                           'starttls': status})
        self._starttls_status_received = True

        if status:
            self._task_queue.put(self.connid.upgrade_ssl)

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

    def disconnect(self):
        self._ctiserver.disconnect_iface(self, DisconnectCause.by_client)

    def disconnected(self, cause):
        logger.info('disconnected %s', cause)
        self._auth_handler.logoff()
        try:
            user_service_manager = context.get('user_service_manager')
            if DisconnectCause.is_valid(cause):
                user_id = self.user_id()
                user_uuid = self._auth_handler.user_uuid()
                user_service_manager.disconnect_no_action(user_id, user_uuid)
            else:
                raise TypeError('invalid DisconnectCause %s' % cause)
        except NotLoggedException:
            'not so exceptionnal, a connection has been closed before login in'

    def manage_connection(self, msg):
        replies = []
        commands = self._cti_msg_decoder.decode(msg)
        for command in commands:
            replies.extend(self._run_functions(command))
        return replies

    def _is_authenticated(self):
        return self._auth_handler.is_authenticated()

    def _run_functions(self, decoded_command):
        no_auth_commands = ['login_id', 'login_pass', 'starttls']
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

    def _on_auth_success(self):
        self._broadcast_cti_group.add(self)
        user_id = self._auth_handler.user_id()
        self.connection_details.update({'userid': user_id,
                                        'user_uuid': self._auth_handler.user_uuid(),
                                        'auth_token': self._auth_handler.auth_token(),
                                        'authenticated': self._auth_handler.is_authenticated()})
        self._update_answer_cb(user_id)

    def _update_answer_cb(self, user_id):
        device_manager = context.get('device_manager')
        try:
            device_id = user_db.get_device_id(user_id)
            self._async_runner.run_with_cb(self.set_answer_cb, device_manager.get_answer_fn, device_id)
        except LookupError:
            return

    def set_answer_cb(self, cb):
        if cb:
            self.answer_cb = cb
