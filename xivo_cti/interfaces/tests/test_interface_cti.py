# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
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

from concurrent import futures
from mock import Mock
from mock import patch
from mock import sentinel
from hamcrest import assert_that
from hamcrest import equal_to

from xivo_cti.async_runner import AsyncRunner, synchronize
from xivo_cti.task_queue import new_task_queue
from xivo_cti.ctiserver import CTIServer
from xivo_cti.exception import NoSuchUserException
from xivo_cti.interfaces.interface_cti import CTI, TWO_MONTHS
from xivo_cti.interfaces.interface_cti import NotLoggedException
from xivo_cti.services.device.manager import DeviceManager
from xivo_cti.cti.cti_message_codec import CTIMessageDecoder,\
    CTIMessageEncoder


class TestCTI(unittest.TestCase):

    def setUp(self):
        self.task_queue = new_task_queue()
        self.async_runner = AsyncRunner(futures.ThreadPoolExecutor(max_workers=1), self.task_queue)
        self._ctiserver = Mock(CTIServer, myipbxid='xivo')

        with patch('xivo_cti.interfaces.interface_cti.context', {'async_runner': self.async_runner,
                                                                 'task_queue': self.task_queue}):
            with patch('xivo_cti.interfaces.interface_cti.config', {'auth': {'backend': 'xivo_user'}}):
                self._cti_connection = CTI(self._ctiserver, CTIMessageDecoder(), CTIMessageEncoder())
                self._cti_connection.send_message = Mock()
        self._cti_connection.login_task = Mock()

    def test_user_id_not_connected(self):
        self.assertRaises(NotLoggedException, self._cti_connection.user_id)

    def test_user_id(self):
        user_id = 5
        self._cti_connection.connection_details['userid'] = user_id

        result = self._cti_connection.user_id()

        self.assertEqual(result, user_id)

    @patch('xivo_cti.interfaces.interface_cti.AuthClient')
    @patch.dict('xivo_cti.interfaces.interface_cti.config', {'auth': {'backend': 'xivo_user'}})
    def test_login_pass_wrong_password(self, AuthClient):
        auth_client = AuthClient.return_value
        response = Mock(status_code=401)
        auth_client.token.new.side_effect = requests.exceptions.HTTPError(response=response)
        password = 'secre7'

        with patch.object(self._cti_connection, 'connection_details', {'prelogin': {'username': 'foobar'}}):
            with synchronize(self.async_runner):
                self._cti_connection.receive_login_pass(password, self._cti_connection)

        AuthClient.assert_called_once_with(username='foobar', password=password, backend='xivo_user')
        auth_client.token.new.assert_called_once_with('xivo_user', expiration=TWO_MONTHS)
        self._cti_connection.send_message.assert_called_once_with({'class': 'login_pass',
                                                                   'error_string': 'login_password'})

    @patch('xivo_cti.interfaces.interface_cti.AuthClient')
    @patch.dict('xivo_cti.interfaces.interface_cti.config', {'auth': {'backend': 'xivo_user'}})
    def test_login_pass_auth_error(self, AuthClient):
        auth_client = AuthClient.return_value
        response = Mock(status_code=404)
        auth_client.token.new.side_effect = requests.exceptions.HTTPError(response=response)
        password = 'secre7'

        with patch.object(self._cti_connection, 'connection_details', {'prelogin': {'username': 'foobar'}}):
            with synchronize(self.async_runner):
                self._cti_connection.receive_login_pass(password, self._cti_connection)

        self._cti_connection.send_message.assert_called_once_with({'class': 'login_pass',
                                                                   'error_string': 'xivo_auth_error'})
        AuthClient.assert_called_once_with(username='foobar', password=password, backend='xivo_user')
        auth_client.token.new.assert_called_once_with('xivo_user', expiration=TWO_MONTHS)

    @patch('xivo_cti.interfaces.interface_cti.AuthClient')
    @patch.dict('xivo_cti.interfaces.interface_cti.config', {'auth': {'backend': 'xivo_user'}})
    def test_login_pass_unknown_user(self, AuthClient):
        auth_client = AuthClient.return_value
        auth_client.return_value = {'token': sentinel.token,
                                    'xivo_user_uuid': sentinel.uuid}

        with patch('xivo_cti.interfaces.interface_cti.dao') as dao:
            dao.user.get_by_uuid.side_effect = NoSuchUserException
            with patch.object(self._cti_connection, 'connection_details', {'prelogin': {'username': 'foobar'}}):
                with synchronize(self.async_runner):
                    self._cti_connection.receive_login_pass(sentinel.password, self._cti_connection)

        self._cti_connection.send_message.assert_called_once_with({'class': 'login_pass',
                                                                   'error_string': 'user_not_found'})

    @patch('xivo_cti.interfaces.interface_cti.AuthClient')
    @patch.dict('xivo_cti.interfaces.interface_cti.config', {'auth': {'backend': 'xivo_user'}})
    def test_login_pass_success(self, AuthClient):
        auth_client = AuthClient.return_value
        auth_client.return_value = {'token': sentinel.token,
                                    'xivo_user_uuid': sentinel.uuid}
        password = 'secre7'
        cti_profile_id = 42
        user_config = {'cti_profile_id': cti_profile_id,
                       'enableclient': '1',
                       'id': '1'}

        with patch('xivo_cti.interfaces.interface_cti.dao') as dao:
            dao.user.get_by_uuid.return_value = user_config
            with patch.object(self._cti_connection, 'connection_details', {'prelogin': {'username': 'foobar'}}):
                with patch.object(self._cti_connection, '_get_answer_cb', Mock()):
                    with synchronize(self.async_runner):
                        self._cti_connection.receive_login_pass(password, self._cti_connection)

        AuthClient.assert_called_once_with(username='foobar', password=password, backend='xivo_user')
        auth_client.token.new.assert_called_once_with('xivo_user', expiration=TWO_MONTHS)
        self._cti_connection.send_message.assert_called_once_with({'class': 'login_pass',
                                                                   'capalist': [cti_profile_id]})

    @patch('xivo_cti.interfaces.interface_cti.AuthClient')
    @patch.dict('xivo_cti.interfaces.interface_cti.config', {'auth': {'backend': 'xivo_user'}})
    def test_login_pass_no_profile(self, AuthClient):
        auth_client = AuthClient.return_value
        auth_client.return_value = {'token': sentinel.token,
                                    'xivo_user_uuid': sentinel.uuid}
        password = 'secre7'
        user_config = {'id': '1',
                       'enableclient': '1'}

        with patch('xivo_cti.interfaces.interface_cti.dao') as dao:
            dao.user.get_by_uuid.return_value = user_config
            with patch.object(self._cti_connection, 'connection_details', {'prelogin': {'username': 'foobar'}}):
                with patch.object(self._cti_connection, '_get_answer_cb', Mock()):
                    with synchronize(self.async_runner):
                        self._cti_connection.receive_login_pass(password, self._cti_connection)

        self._cti_connection.send_message.assert_called_once_with({'class': 'login_pass',
                                                                   'error_string': 'capaid_undefined'})

    @patch('xivo_cti.interfaces.interface_cti.AuthClient')
    @patch.dict('xivo_cti.interfaces.interface_cti.config', {'auth': {'backend': 'xivo_user'}})
    def test_login_pass_client_disabled(self, AuthClient):
        auth_client = AuthClient.return_value
        auth_client.return_value = {'token': sentinel.token,
                                    'xivo_user_uuid': sentinel.uuid}
        password = 'secre7'
        cti_profile_id = 42
        user_config = {'cti_profile_id': cti_profile_id,
                       'id': '1',
                       'enableclient': 0}

        with patch('xivo_cti.interfaces.interface_cti.dao') as dao:
            dao.user.get_by_uuid.return_value = user_config
            with patch.object(self._cti_connection, 'connection_details', {'prelogin': {'username': 'foobar'}}):
                with patch.object(self._cti_connection, '_get_answer_cb', Mock()):
                    with synchronize(self.async_runner):
                        self._cti_connection.receive_login_pass(password, self._cti_connection)

        self._cti_connection.send_message.assert_called_once_with({'class': 'login_pass',
                                                                   'error_string': 'login_password'})
