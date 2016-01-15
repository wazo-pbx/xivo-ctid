# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

import requests

import xivo_cti

from datetime import timedelta

from xivo_auth_client import Client as AuthClient

from xivo_cti import config
from xivo_cti import dao
from xivo_cti.exception import NoSuchUserException
from xivo_cti.ioc.context import context
from xivo_cti.cti.commands.login import (LoginID, LoginPass)

TWO_MONTHS = timedelta(days=60).total_seconds()

logger = logging.getLogger(__name__)


class AuthentificationHandler(object):

    _session_id_len = 10

    def __init__(self, connection, on_complete_cb):
        self._connection = connection
        self._session_id = self._new_session_id()
        self._auth_backend = config['auth']['backend']
        self._auth_config = config['auth']
        self._async_runner = context.get('async_runner')
        self._task_queue = context.get('task_queue')
        self._auth_token = None
        self._authenticated = False
        self._on_complete_cb = on_complete_cb

    def auth_token(self):
        return self._auth_token

    def is_authenticated(self):
        return self._authenticated

    def run(self):
        LoginID.register_callback_params(self._on_login_id, ['userlogin',
                                                             'xivo_version',
                                                             'cti_connection'])

    def logoff(self):
        self._is_authenticated = False
        if self._auth_token and self._auth_client:
            self._async_runner.run(self._auth_client.token.revoke, self._auth_token)

    def user_id(self):
        if self._authenticated:
            return self._user_id

    def user_uuid(self):
        if self._authenticated:
            return self._user_uuid

    def _create_token(self, auth_client, backend, username):
        try:
            return auth_client.token.new(backend, expiration=TWO_MONTHS)
        except requests.exceptions.RequestException as e:
            if e.response and e.response.status_code == 401:
                logger.info('Authentification failed, got a 401 from xivo-auth username: %s backend: %s',
                            username, backend)
                error_string = 'login_password'
            else:
                logger.exception('Unexpected xivo-auth error')
                error_string = 'xivo_auth_error'

            self._task_queue.put(self._fatal, 'login_pass', error_string)

    def _fatal(self, msg_class, error_string):
        msg = {'class': msg_class,
               'error_string': error_string}
        self._send_msg(msg)
        self._connection.disconnect()

    def _on_auth_complete(self):
        if self._on_complete_cb:
            self._on_complete_cb()

    def _on_auth_success(self, token_data):
        if not token_data:
            return

        self._user_uuid = token_data['xivo_user_uuid']
        try:
            user_config = dao.user.get_by_uuid(self._user_uuid)
        except NoSuchUserException:
            return self._fatal('login_pass', 'user_not_found')

        client_enabled = user_config.get('enableclient', 0) != 0
        cti_profile_id = user_config.get('cti_profile_id')
        if not client_enabled or not cti_profile_id:
            logger.info('%s failed to login, client enabled %s profile %s',
                        self._username, client_enabled, cti_profile_id)
            return self._fatal('login_pass', 'login_password')

        self._authenticated = True
        self._auth_token = token_data['token']
        self._user_id = str(user_config['id'])
        msg = self._new_login_pass_reply(cti_profile_id)
        self._send_msg(msg)
        self._on_auth_complete()

    def _on_login_id(self, userlogin, xivo_version, cti_connection):
        if cti_connection != self._connection:
            return

        LoginID.deregister_callback(self._on_login_id)

        if xivo_version != xivo_cti.CTI_PROTOCOL_VERSION:
            msg = 'xivoversion_client:{};{}'.format(xivo_version, xivo_cti.CTI_PROTOCOL_VERSION)
            self._fatal('login_id', msg)
            return

        self._username = userlogin

        LoginPass.register_callback_params(self._on_login_pass, ['password',
                                                                 'cti_connection'])

        msg = self._new_login_id_reply()
        self._send_msg(msg)

    def _on_login_pass(self, password, cti_connection):
        if cti_connection != self._connection:
            return

        LoginPass.deregister_callback(self._on_login_pass)

        self._auth_client = AuthClient(username=self._username, password=password, **self._auth_config)
        self._async_runner.run_with_cb(self._on_auth_success,
                                       self._create_token,
                                       self._auth_client, self._auth_backend, self._username)

    def _new_login_id_reply(self):
        return {'class': 'login_id',
                'sessionid': self._session_id,
                'xivoversion': xivo_cti.CTI_PROTOCOL_VERSION}

    def _new_login_pass_reply(self, cti_profile_id):
        return {'class': 'login_pass', 'capalist': [cti_profile_id]}

    def _new_session_id(self):
        return ''.join(random.sample(xivo_cti.ALPHANUMS, self._session_id_len))

    def _send_msg(self, msg):
        self._connection.send_message(msg)
