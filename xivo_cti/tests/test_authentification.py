# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
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

from hamcrest import (assert_that, equal_to, has_length, is_)
from mock import (Mock, patch)
from mock import sentinel as s

from xivo_cti import CTI_PROTOCOL_VERSION
from xivo_cti.async_runner import AsyncRunner
from xivo_cti.exception import NoSuchUserException
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.services.user.manager import UserServiceManager

from ..authentication import AuthenticationHandler


TWO_MONTHS = timedelta(days=60).total_seconds()


class _BaseAuthenticationHandlerTestCase(unittest.TestCase):

    def setUp(self):
        self.connection = Mock(CTI)
        self.async_runner = Mock(AsyncRunner)
        self.task_queue = Mock()
        self.task_scheduler = Mock()
        self.complete_cb = Mock()
        with patch('xivo_cti.authentication.context', {'async_runner': self.async_runner,
                                                       'task_queue': self.task_queue,
                                                       'task_scheduler': self.task_scheduler}):
            with patch('xivo_cti.authentication.config', {'auth': {'backend': s.backend,
                                                                   'host': s.host},
                                                          'client': {'login_timeout': 42}}):
                self.handler = AuthenticationHandler(self.connection, self.complete_cb)
        self.session_id = self.handler._session_id
        self.handler._username = s.username

    def assert_message_sent(self, msg):
        self.connection.send_message.assert_called_once_with(msg)

    def assert_no_message_sent(self):
        assert_that(self.connection.send_message.called, is_(False))

    def assert_fatal(self, message_class, error_string):
        msg = {'class': message_class,
               'error_string': error_string}
        self.assert_message_sent(msg)

    def assert_fatal_scheduled(self, message_class, error_string):
        self.task_queue.put.assert_called_once_with(self.handler._fatal, message_class, error_string)


class TestAuthenticationHandler(_BaseAuthenticationHandlerTestCase):

    @patch('xivo_cti.authentication.LoginID')
    def test_that_run_starts_the_login_chain(self, LoginID):
        self.handler.run()

        LoginID.register_callback_params.assert_called_once_with(
            self.handler._on_login_id,
            ['userlogin', 'xivo_version', 'cti_connection'])

    @patch('xivo_cti.authentication.LoginID', Mock())
    def test_that_run_starts_the_login_timeout_task(self):
        self.handler.run()

        self.task_scheduler.schedule(42, self.handler._on_cti_login_auth_timeout)

    def test_that_is_authenticated_is_false(self):
        result = self.handler.is_authenticated()

        assert_that(result, equal_to(False))

    def test_new_session_id(self):
        session_id = self.handler._new_session_id()

        assert_that(session_id, has_length(10))


class TestAuthenticationHandlerOnLoginID(_BaseAuthenticationHandlerTestCase):

    def test_that_on_login_id_checks_the_version(self):
        bad_version = CTI_PROTOCOL_VERSION + '1'

        self.handler._on_login_id(s.login, bad_version, self.connection)

        expected_msg = {'class': 'login_id',
                        'error_string': 'xivoversion_client:%s;%s' % (bad_version, CTI_PROTOCOL_VERSION)}
        self.assert_message_sent(expected_msg)

    @patch('xivo_cti.authentication.LoginPass')
    def test_that_login_pass_is_registered_on_success(self, LoginPass):
        self.handler._on_login_id(s.login, CTI_PROTOCOL_VERSION, self.connection)

        LoginPass.register_callback_params.assert_called_once_with(
            self.handler._on_login_pass,
            ['password', 'cti_connection'])

    @patch('xivo_cti.authentication.LoginID')
    def test_that_login_id_is_deregistered(self, LoginID):
        self.handler._on_login_id(s.login, CTI_PROTOCOL_VERSION, self.connection)

        LoginID.deregister_callback.assert_called_once_with(self.handler._on_login_id)

    def test_that_a_reply_is_sent_when_successfull(self):
        self.handler._on_login_id(s.login, CTI_PROTOCOL_VERSION, self.connection)

        expected_msg = {'class': 'login_id',
                        'sessionid': self.session_id,
                        'xivoversion': CTI_PROTOCOL_VERSION}
        self.assert_message_sent(expected_msg)

    @patch('xivo_cti.authentication.LoginPass')
    @patch('xivo_cti.authentication.LoginID')
    def test_that_nothing_happens_if_another_connection(self, LoginID, LoginPass):
        another_connection = Mock(CTI)

        self.handler._on_login_id(s.login, CTI_PROTOCOL_VERSION, another_connection)

        assert_that(LoginID.deregister_callback.called, is_(False))
        assert_that(LoginPass.register_callback_params.called, is_(False))
        self.assert_no_message_sent()


class TestAuthenticationHandlerOnLoginPass(_BaseAuthenticationHandlerTestCase):

    @patch('xivo_cti.authentication.LoginPass')
    def test_that_login_pass_is_deregistered(self, LoginPass):
        self.handler._on_login_pass(s.password, self.connection)

        LoginPass.deregister_callback.assert_called_once_with(self.handler._on_login_pass)

    @patch('xivo_cti.authentication.AuthClient')
    def test_that_create_token_is_scheduled(self, AuthClient):
        auth_client = AuthClient.return_value

        self.handler._on_login_pass(s.password, self.connection)

        self.async_runner.run_with_cb.assert_called_once_with(
            self.handler._on_auth_success,
            self.handler._create_token,
            auth_client, s.backend, s.username)
        assert_that(self.handler._auth_client, equal_to(auth_client))

    @patch('xivo_cti.authentication.LoginPass')
    @patch('xivo_cti.authentication.AuthClient')
    def test_that_nothing_happens_if_another_connection(self, LoginPass, AuthClient):
        another_connection = Mock(CTI)

        self.handler._on_login_pass(s.password, another_connection)

        assert_that(LoginPass.deregister_callback.called, is_(False))
        assert_that(AuthClient.called, is_(False))
        assert_that(self.async_runner.run_with_cb.called, is_(False))


class TestAuthenticationHandlerCreateToken(_BaseAuthenticationHandlerTestCase):

    def setUp(self):
        super(TestAuthenticationHandlerCreateToken, self).setUp()
        self.auth_client = Mock()

    def test_that_create_token_returns_the_clients_return_value(self):
        expiration = TWO_MONTHS

        result = self.handler._create_token(self.auth_client, s.backend, s.username)

        assert_that(result, equal_to(self.auth_client.token.new.return_value))
        self.auth_client.token.new.assert_called_once_with(s.backend, expiration=expiration)

    def test_401_from_wazo_auth(self):
        exception = requests.exceptions.RequestException(response=Mock(status_code=401))
        self.auth_client.token.new.side_effect = exception

        self.handler._create_token(self.auth_client, s.backend, s.username)

        self.assert_fatal_scheduled('login_pass', 'login_password')

    def test_requests_exception_from_wazo_auth(self):
        exception = requests.exceptions.RequestException()
        self.auth_client.token.new.side_effect = exception

        self.handler._create_token(self.auth_client, s.backend, s.username)

        self.assert_fatal_scheduled('login_pass', 'xivo_auth_error')


class TestAuthenticationHandlerOnAuthSuccess(_BaseAuthenticationHandlerTestCase):

    def setUp(self):
        super(TestAuthenticationHandlerOnAuthSuccess, self).setUp()
        self.user_config = {'cti_profile_id': s.profile_id,
                            'enableclient': '1',
                            'id': 1}
        self.token_data = {'xivo_user_uuid': s.uuid,
                           'token': s.token}

    @patch('xivo_cti.authentication.dao')
    def test_login_pass_reply_on_success(self, dao):
        dao.user.get_by_uuid.return_value = self.user_config

        self.handler._on_auth_success(self.token_data)

        self.assert_message_sent({'class': 'login_pass',
                                  'capalist': [s.profile_id]})

    @patch('xivo_cti.authentication.dao')
    def test_is_authenticated_on_success(self, dao):
        dao.user.get_by_uuid.return_value = self.user_config

        self.handler._on_auth_success(self.token_data)
        result = self.handler.is_authenticated()

        assert_that(result, equal_to(True))

    @patch('xivo_cti.authentication.dao')
    def test_that_auth_token_is_set_on_success(self, dao):
        dao.user.get_by_uuid.return_value = self.user_config

        self.handler._on_auth_success(self.token_data)
        result = self.handler.auth_token()

        assert_that(result, equal_to(s.token))

    @patch('xivo_cti.authentication.dao')
    def test_that_user_id_and_uuid_are_set_on_success(self, dao):
        dao.user.get_by_uuid.return_value = self.user_config

        self.handler._on_auth_success(self.token_data)

        assert_that(self.handler._user_uuid, equal_to(s.uuid))
        assert_that(self.handler._user_id, equal_to('1'))

    @patch('xivo_cti.authentication.LoginCapas')
    @patch('xivo_cti.authentication.dao')
    def test_that_login_capas_command_is_registered_on_success(self, dao, LoginCapas):
        dao.user.get_by_uuid.return_value = self.user_config

        self.handler._on_auth_success(self.token_data)

        LoginCapas.register_callback_params.assert_called_once_with(
            self.handler._on_login_capas,
            ['capaid', 'state', 'cti_connection'])

    @patch('xivo_cti.authentication.dao')
    def test_complete_cb_are_called_on_success(self, dao):
        dao.user.get_by_uuid.return_value = self.user_config

        self.handler._on_auth_success(self.token_data)

        self.complete_cb.assert_called_once_with()

    def test_that_nothing_happens_on_create_token_error(self):
        self.handler._on_auth_success(None)

        assert_that(self.handler.is_authenticated(), equal_to(False))

    @patch('xivo_cti.authentication.dao')
    def test_unknown_user(self, dao):
        dao.user.get_by_uuid.side_effect = NoSuchUserException

        self.handler._on_auth_success(self.token_data)

        self.assert_fatal('login_pass', 'user_not_found')

    @patch('xivo_cti.authentication.dao')
    def test_disabled_client(self, dao):
        user_config = dict(self.user_config)
        user_config['enableclient'] = 0
        dao.user.get_by_uuid.return_value = user_config

        self.handler._on_auth_success(self.token_data)

        self.assert_fatal('login_pass', 'login_password')

    @patch('xivo_cti.authentication.dao')
    def test_undefined_profile(self, dao):
        user_config = dict(self.user_config)
        user_config.pop('cti_profile_id', None)
        dao.user.get_by_uuid.return_value = user_config

        self.handler._on_auth_success(self.token_data)

        self.assert_fatal('login_pass', 'login_password')


@patch('xivo_cti.authentication.context', Mock())
class TestAuthenticationHandlerOnLoginCapas(_BaseAuthenticationHandlerTestCase):

    xivo_user_status = {u'available': {'color': u'#9BC920',
                                       'allowed': [u'available',
                                                   u'away',
                                                   u'outtolunch',
                                                   u'donotdisturb',
                                                   u'berightback'],
                                       'actions': {u'enablednd': u'false'},
                                       'longname': u'Disponible'},
                        u'berightback': {'color': u'#FFB545',
                                         'allowed': [u'available',
                                                     u'away',
                                                     u'outtolunch',
                                                     u'donotdisturb',
                                                     u'berightback'],
                                         'actions': {u'enablednd': u'false'},
                                         'longname': u'Bient\xf4t de retour'},
                        u'disconnected': {'color': u'#9E9E9E',
                                          'actions': {u'agentlogoff': u''},
                                          'longname': u'D\xe9connect\xe9'},
                        u'away': {'color': u'#FFDD00',
                                  'allowed': [u'available',
                                              u'away',
                                              u'outtolunch',
                                              u'donotdisturb',
                                              u'berightback'],
                                  'actions': {u'enablednd': u'false'},
                                  'longname': u'Sorti'},
                        u'donotdisturb': {'color': u'#D13224',
                                          'allowed': [u'available',
                                                      u'away',
                                                      u'outtolunch',
                                                      u'donotdisturb',
                                                      u'berightback'],
                                          'actions': {u'enablednd': u'true'},
                                          'longname': u'Ne pas d\xe9ranger'},
                        u'outtolunch': {'color': u'#6CA6FF',
                                        'allowed': [u'available',
                                                    u'away',
                                                    u'outtolunch',
                                                    u'donotdisturb',
                                                    u'berightback'],
                                        'actions': {u'enablednd': u'false'},
                                        'longname': u'Parti Manger'}}

    xivo_phone_status = {u'16': {'color': u'#FFDD00',
                                 'longname': u'En Attente'},
                         u'1': {'color': u'#D13224',
                                'longname': u'En ligne OU appelle'},
                         u'0': {'color': u'#9BC920',
                                'longname': u'Disponible'},
                         u'2': {'color': u'#D13224',
                                'longname': u'Occup\xe9'},
                         u'-1': {'color': u'#9E9E9E',
                                 'longname': u'D\xe9sactiv\xe9'},
                         u'4': {'color': u'#9E9E9E',
                                'longname': u'Indisponible'},
                         u'-2': {'color': u'#9E9E9E',
                                 'longname': u'Inexistant'},
                         u'9': {'color': u'#D13224',
                                'longname': u'(En Ligne OU Appelle) ET Sonne'},
                         u'8': {'color': u'#6CA6FF', 'longname': u'Sonne'}}

    client_xlets = [[u'identity', u'grid'],
                    [u'tabber', u'grid', '1'],
                    [u'customerinfo', u'tab', '1'],
                    [u'fax', u'tab', '2'],
                    [u'history', u'tab', '3'],
                    [u'features', u'tab', '5'],
                    [u'conference', u'tab', '7'],
                    [u'people', u'tab', '8']]

    config = {'profiles': {1: {'preferences': u'itm_preferences_Supervisor',
                               'userstatus': u'xivo',
                               'services': u'itm_services_Supervisor',
                               'phonestatus': u'xivo',
                               'xlets': [[u'identity', u'grid'],
                                         [u'queueentrydetails', u'dock', 'fcms'],
                                         [u'agentdetails', u'dock', 'fcms'],
                                         [u'queues', u'dock', 'fcms'],
                                         [u'queuemembers', u'dock', 'fcms'],
                                         [u'agents', u'dock', 'fcms']],
                               'id': 1,
                               'name': u'Supervisor'},
                           2: {'preferences': u'itm_preferences_Agent',
                               'userstatus': u'xivo',
                               'services': u'itm_services_Agent',
                               'phonestatus': u'xivo',
                               'xlets': [[u'identity', u'grid'],
                                         [u'queues', u'dock', 'fcms'],
                                         [u'customerinfo', u'dock', 'fcms'],
                                         [u'agentdetails', u'dock', 'fcms']],
                               'id': 2,
                               'name': u'Agent'},
                           3: {'preferences': u'itm_preferences_Client',
                               'userstatus': u'xivo',
                               'services': u'itm_services_Client',
                               'phonestatus': u'xivo',
                               'xlets': client_xlets,
                               'id': 3,
                               'name': u'Client'},
                           4: {'preferences': u'itm_preferences_Switchboard',
                               'userstatus': u'xivo',
                               'services': u'itm_services_Switchboard',
                               'phonestatus': u'xivo',
                               'xlets': [[u'identity', u'grid'],
                                         [u'switchboard', u'dock', 'fcms', '1'],
                                         [u'directory', u'dock', 'fcms', '3']],
                               'id': 4,
                               'name': u'Switchboard'}},
              'services': {u'itm_services_Switchboard': [''],
                           u'itm_services_Agent': [''],
                           u'itm_services_Client': [u'enablednd', u'fwdunc', u'fwdbusy', u'fwdrna'],
                           u'itm_services_Supervisor': ['']},
              'preferences': {u'itm_preferences_Client': False,
                              u'itm_preferences_Supervisor': False,
                              u'itm_preferences_Agent': False,
                              u'itm_preferences_Switchboard': False},
              'userstatus': {'xivo': xivo_user_status},
              'phonestatus': {'xivo': xivo_phone_status}}

    def setUp(self):
        super(TestAuthenticationHandlerOnLoginCapas, self).setUp()
        self.handler._user_uuid = s.uuid
        self.handler._auth_token = s.token
        self.user_id = self.handler._user_id = 42
        self.profile_id = self.handler._cti_profile_id = 3
        self.connection.login_task = Mock()

    def test_login_capas_reply_on_success(self):
        ipbxid = 'xivo'
        capas = {'services': [u'enablednd', u'fwdunc', u'fwdbusy', u'fwdrna'],
                 'preferences': False,
                 'userstatus': self.xivo_user_status,
                 'phonestatus': self.xivo_phone_status}
        capaxlets = self.client_xlets
        state = 'available'

        with patch('xivo_cti.authentication.config', self.config):
            self.handler._on_login_capas(self.profile_id, state, self.connection)

        msg = {'class': 'login_capas',
               'userid': self.user_id,
               'ipbxid': ipbxid,
               'capas': capas,
               'capaxlets': capaxlets,
               'appliname': 'Client'}
        self.assert_message_sent(msg)

    def test_that_the_login_task_is_cancelled_on_success(self):
        with patch.object(self.handler, '_login_task') as login_task:
            with patch('xivo_cti.authentication.config', self.config):
                self.handler._on_login_capas(self.profile_id, 'available', self.connection)

        login_task.cancel.assert_called_once_with()

    def test_that_the_user_status_is_updated_on_success(self):
        user_service_manager = Mock(UserServiceManager)
        state = 'available'

        with patch('xivo_cti.authentication.context', {'user_service_manager': user_service_manager}):
            with patch('xivo_cti.authentication.config', self.config):
                self.handler._on_login_capas(self.profile_id, state, self.connection)

        user_service_manager.connect.assert_called_once_with(self.user_id, s.uuid, s.token, state)

    @patch('xivo_cti.authentication.LoginCapas')
    def test_that_login_capas_command_is_deregistered(self, LoginCapas):
        with patch('xivo_cti.authentication.config', self.config):
            self.handler._on_login_capas(self.profile_id, 'available', self.connection)

        LoginCapas.deregister_callback.assert_called_once_with(self.handler._on_login_capas)

    def test_with_a_capaid_that_does_not_match_the_users_profile(self):
        with patch('xivo_cti.authentication.config', self.config):
            self.handler._on_login_capas(1, 'available', self.connection)

        self.assert_fatal('login_capas', 'wrong cti_profile_id')

    def test_with_an_unknown_profile(self):
        unknown_profile_id = 42

        with patch.object(self.handler, '_cti_profile_id', unknown_profile_id):
            with patch('xivo_cti.authentication.config', self.config):
                self.handler._on_login_capas(unknown_profile_id, 'available', self.connection)

        self.assert_fatal('login_capas', 'unknown cti_profile_id')

    def test_that_nothing_happens_if_another_connection(self):
        another_connection = Mock(CTI)

        with patch('xivo_cti.authentication.config', self.config):
            self.handler._on_login_capas(s.capaid, s.state, another_connection)

        self.assert_no_message_sent()
