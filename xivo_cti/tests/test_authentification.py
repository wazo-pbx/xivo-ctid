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

import unittest

import requests

from datetime import timedelta

from hamcrest import (assert_that, equal_to, has_length)
from mock import (Mock, patch)
from mock import sentinel as s

from xivo_cti import CTI_PROTOCOL_VERSION
from xivo_cti.async_runner import AsyncRunner
from xivo_cti.exception import NoSuchUserException
from xivo_cti.interfaces.interface_cti import CTI

from ..authentification import AuthentificationHandler


TWO_MONTHS = timedelta(days=60).total_seconds()


class _BaseAuthentificationHandlerTestCase(unittest.TestCase):

    def setUp(self):
        self.connection = Mock(CTI)
        self.async_runner = Mock(AsyncRunner)
        self.task_queue = Mock()
        self.complete_cb = Mock()
        with patch('xivo_cti.authentification.context', {'async_runner': self.async_runner,
                                                         'task_queue': self.task_queue}):
            with patch('xivo_cti.authentification.config', {'auth': {'backend': s.backend,
                                                                     'host': s.host}}):
                self.handler = AuthentificationHandler(self.connection, self.complete_cb)
        self.session_id = self.handler._session_id
        self.handler._username = s.username

    def assert_disconnect_called(self):
        self.connection.disconnect.assert_called_once_with()

    def assert_message_sent(self, msg):
        self.connection.send_message.assert_called_once_with(msg)

    def assert_no_message_sent(self):
        assert_that(self.connection.send_message.call_count, equal_to(0))

    def assert_fatal(self, message_class, error_string):
        msg = {'class': message_class,
               'error_string': error_string}
        self.assert_message_sent(msg)
        self.assert_disconnect_called()

    def assert_fatal_scheduled(self, message_class, error_string):
        self.task_queue.put.assert_called_once_with(self.handler._fatal, message_class, error_string)


class TestAuthentificationHandler(_BaseAuthentificationHandlerTestCase):

    @patch('xivo_cti.authentification.LoginID')
    def test_that_run_starts_the_login_chain(self, LoginID):
        self.handler.run()

        LoginID.register_callback_params.assert_called_once_with(
            self.handler._on_login_id,
            ['userlogin', 'xivo_version', 'cti_connection'])

    def test_that_is_authenticated_is_false(self):
        result = self.handler.is_authenticated()

        assert_that(result, equal_to(False))

    def test_new_session_id(self):
        session_id = self.handler._new_session_id()

        assert_that(session_id, has_length(10))


class TestAuthentificationHandlerCreateToken(_BaseAuthentificationHandlerTestCase):

    def setUp(self):
        super(TestAuthentificationHandlerCreateToken, self).setUp()
        self.auth_client = Mock()

    def test_that_create_token_returns_the_clients_return_value(self):
        expiration = TWO_MONTHS

        result = self.handler._create_token(self.auth_client, s.backend, s.username)

        assert_that(result, equal_to(self.auth_client.token.new.return_value))
        self.auth_client.token.new.assert_called_once_with(s.backend, expiration=expiration)

    def test_401_from_xivo_auth(self):
        exception = requests.exceptions.RequestException(response=Mock(status_code=401))
        self.auth_client.token.new.side_effect = exception

        self.handler._create_token(self.auth_client, s.backend, s.username)

        self.assert_fatal_scheduled('login_pass', 'login_password')

    def test_requests_exception_from_xivo_auth(self):
        exception = requests.exceptions.RequestException()
        self.auth_client.token.new.side_effect = exception

        self.handler._create_token(self.auth_client, s.backend, s.username)

        self.assert_fatal_scheduled('login_pass', 'xivo_auth_error')


class TestAuthentificationHandlerOnAuthSuccess(_BaseAuthentificationHandlerTestCase):

    def setUp(self):
        super(TestAuthentificationHandlerOnAuthSuccess, self).setUp()
        self.user_config = {'cti_profile_id': s.profile_id,
                            'enableclient': '1',
                            'id': 1}
        self.token_data = {'xivo_user_uuid': s.uuid,
                           'token': s.token}

    @patch('xivo_cti.authentification.dao')
    def test_login_pass_reply_on_success(self, dao):
        dao.user.get_by_uuid.return_value = self.user_config

        self.handler._on_auth_success(self.token_data)

        self.assert_message_sent({'class': 'login_pass',
                                  'capalist': [s.profile_id]})

    @patch('xivo_cti.authentification.dao')
    def test_is_authenticated_on_success(self, dao):
        dao.user.get_by_uuid.return_value = self.user_config

        self.handler._on_auth_success(self.token_data)
        result = self.handler.is_authenticated()

        assert_that(result, equal_to(True))

    @patch('xivo_cti.authentification.dao')
    def test_that_auth_token_is_set_on_success(self, dao):
        dao.user.get_by_uuid.return_value = self.user_config

        self.handler._on_auth_success(self.token_data)
        result = self.handler.auth_token()

        assert_that(result, equal_to(s.token))

    @patch('xivo_cti.authentification.dao')
    def test_that_user_id_and_uuid_are_set_on_success(self, dao):
        dao.user.get_by_uuid.return_value = self.user_config

        self.handler._on_auth_success(self.token_data)

        assert_that(self.handler._user_uuid, equal_to(s.uuid))
        assert_that(self.handler._user_id, equal_to('1'))

    @patch('xivo_cti.authentification.dao')
    def test_complete_cb_are_called_on_success(self, dao):
        dao.user.get_by_uuid.return_value = self.user_config

        self.handler._on_auth_success(self.token_data)

        self.complete_cb.assert_called_once_with()

    def test_that_nothing_happens_on_create_token_error(self):
        self.handler._on_auth_success(None)

        assert_that(self.handler.is_authenticated(), equal_to(False))

    @patch('xivo_cti.authentification.dao')
    def test_unknown_user(self, dao):
        dao.user.get_by_uuid.side_effect = NoSuchUserException

        self.handler._on_auth_success(self.token_data)

        self.assert_fatal('login_pass', 'user_not_found')

    @patch('xivo_cti.authentification.dao')
    def test_disabled_client(self, dao):
        user_config = dict(self.user_config)
        user_config['enableclient'] = 0
        dao.user.get_by_uuid.return_value = user_config

        self.handler._on_auth_success(self.token_data)

        self.assert_fatal('login_pass', 'login_password')

    @patch('xivo_cti.authentification.dao')
    def test_undefined_profile(self, dao):
        user_config = dict(self.user_config)
        user_config.pop('cti_profile_id', None)
        dao.user.get_by_uuid.return_value = user_config

        self.handler._on_auth_success(self.token_data)

        self.assert_fatal('login_pass', 'login_password')


class TestAuthentificationHandlerOnLoginID(_BaseAuthentificationHandlerTestCase):

    def test_that_on_login_id_checks_the_version(self):
        bad_version = CTI_PROTOCOL_VERSION + '1'

        self.handler._on_login_id(s.login, bad_version, self.connection)

        expected_msg = {'class': 'login_id',
                        'error_string': 'xivoversion_client:%s;%s' % (bad_version, CTI_PROTOCOL_VERSION)}
        self.assert_message_sent(expected_msg)
        self.assert_disconnect_called()

    @patch('xivo_cti.authentification.LoginPass')
    def test_that_login_pass_is_registered_on_success(self, LoginPass):
        self.handler._on_login_id(s.login, CTI_PROTOCOL_VERSION, self.connection)

        LoginPass.register_callback_params.assert_called_once_with(
            self.handler._on_login_pass,
            ['password', 'cti_connection'])

    @patch('xivo_cti.authentification.LoginID')
    def test_that_login_id_is_deregistered(self, LoginID):
        self.handler._on_login_id(s.login, CTI_PROTOCOL_VERSION, self.connection)

        LoginID.deregister_callback.assert_called_once_with(self.handler._on_login_id)

    def test_that_a_reply_is_sent_when_successfull(self):
        self.handler._on_login_id(s.login, CTI_PROTOCOL_VERSION, self.connection)

        expected_msg = {'class': 'login_id',
                        'sessionid': self.session_id,
                        'xivoversion': CTI_PROTOCOL_VERSION}
        self.assert_message_sent(expected_msg)

    @patch('xivo_cti.authentification.LoginPass')
    @patch('xivo_cti.authentification.LoginID')
    def test_that_nothing_happens_if_another_connection(self, LoginID, LoginPass):
        another_connection = Mock(CTI)

        self.handler._on_login_id(s.login, CTI_PROTOCOL_VERSION, another_connection)

        assert_that(LoginID.deregister_callback.call_count, equal_to(0))
        assert_that(LoginPass.register_callback_params.call_count, equal_to(0))
        self.assert_no_message_sent()


class TestAuthentificationHandlerOnLoginPass(_BaseAuthentificationHandlerTestCase):

    @patch('xivo_cti.authentification.LoginPass')
    def test_that_login_pass_is_deregistered(self, LoginPass):
        self.handler._on_login_pass(s.password, self.connection)

        LoginPass.deregister_callback.assert_called_once_with(self.handler._on_login_pass)

    @patch('xivo_cti.authentification.AuthClient')
    def test_that_create_token_is_scheduled(self, AuthClient):
        auth_client = AuthClient.return_value

        self.handler._on_login_pass(s.password, self.connection)

        self.async_runner.run_with_cb.assert_called_once_with(
            self.handler._on_auth_success,
            self.handler._create_token,
            auth_client, s.backend, s.username)
        assert_that(self.handler._auth_client, equal_to(auth_client))

    @patch('xivo_cti.authentification.LoginPass')
    @patch('xivo_cti.authentification.AuthClient')
    def test_that_nothing_happens_if_another_connection(self, LoginPass, AuthClient):
        another_connection = Mock(CTI)

        self.handler._on_login_pass(s.password, another_connection)

        assert_that(LoginPass.deregister_callback.call_count, equal_to(0))
        assert_that(AuthClient.call_count, equal_to(0))
        assert_that(self.async_runner.run_with_cb.call_count, equal_to(0))
