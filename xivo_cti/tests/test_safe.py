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

import unittest

from hamcrest import assert_that, is_
from mock import ANY
from mock import Mock
from mock import patch
from mock import sentinel

from xivo_cti.channel import Channel
from xivo_cti.ctiserver import CTIServer
from xivo_cti.innerdata import Safe, TWO_MONTHS
from xivo_cti.ioc.context import context
from xivo_cti.cti.commands.getlist import ListID, UpdateConfig, UpdateStatus
from xivo_cti.tools.weak_method import WeakCallable
from xivo_cti.cti.commands.availstate import Availstate
from xivo_cti.services.user.manager import UserServiceManager
from xivo_cti.services.queue_member.cti.adapter import QueueMemberCTIAdapter
from xivo_cti.lists.users_list import UsersList


class TestSafe(unittest.TestCase):

    _ipbx_id = 'xivo'
    _auth_config = {
        'host': 'auth-host',
        'port': 4242,
        'key_file': '/tmp/some.yml',
        'service_id': 'some-id',
        'service_key': 'some-key',
    }

    def setUp(self):
        queue_member_cti_adapter = Mock(QueueMemberCTIAdapter)
        self._ctiserver = Mock(CTIServer)
        self.safe = Safe(self._ctiserver, queue_member_cti_adapter)
        self.safe.user_service_manager = Mock(UserServiceManager)

    def test_safe(self):
        self.assertEqual(self.safe._ctiserver, self._ctiserver)

    def test_register_cti_handlers(self):
        context.register('people_cti_adapter', Mock())

        self.safe.register_cti_handlers()

        self.assert_callback_registered(ListID, self.safe.handle_getlist_list_id)
        self.assert_callback_registered(UpdateConfig, self.safe.handle_getlist_update_config)
        self.assert_callback_registered(UpdateStatus, self.safe.handle_getlist_update_status)
        self.assert_callback_registered(Availstate, self.safe.user_service_manager.set_presence)

    def test_handle_getlist_list_id_not_a_list(self):
        ret = self.safe.handle_getlist_list_id('not_a_list', '1')

        self.assertEqual(ret, None)

    def assert_callback_registered(self, cls, fn):
        found = False
        for callback in cls._callbacks_with_params:
            if WeakCallable(fn) == callback[0]:
                found = True
        self.assertTrue(found, 'Could not find callback to function %s' % fn)

    def test_that_user_match_with_no_user_returns_false(self):
        self.safe.xod_config['users'] = Mock(UsersList, keeplist={})

        result = self.safe.user_match(None, {'desttype': 'user',
                                             'destid': '42'})

        assert_that(result, is_(False))

    @patch('xivo_dao.queue_dao.is_user_member_of_queue')
    def test_user_match_with_queue(self, mock_is_user_member_of_queue):
        user_id = 1
        queue_id = 42
        tomatch = {
            'desttype': 'queue',
            'destid': queue_id
        }
        mock_is_user_member_of_queue.return_value = True
        userlist = Mock(UsersList)
        userlist.keeplist = {}
        userlist.keeplist[user_id] = {
            'cti_profile_id': 1,
            'context': 'default',
            'agentid': 22
        }
        self.safe.xod_config = {
            'users': userlist
        }

        domatch = self.safe.user_match(user_id, tomatch)

        mock_is_user_member_of_queue.assert_called_once_with(user_id, queue_id)
        self.assertTrue(domatch)

    @patch('xivo_dao.group_dao.is_user_member_of_group')
    def test_user_match_with_group(self, mock_is_user_member_of_group):
        user_id = 1
        group_id = 42
        tomatch = {
            'desttype': 'group',
            'destid': group_id,
        }
        mock_is_user_member_of_group.return_value = True
        userlist = Mock(UsersList)
        userlist.keeplist = {}
        userlist.keeplist[user_id] = {
            'cti_profile_id': 1,
            'context': 'default',
            'agentid': 22
        }
        self.safe.xod_config = {
            'users': userlist
        }

        domatch = self.safe.user_match(user_id, tomatch)

        mock_is_user_member_of_group.assert_called_once_with(user_id, group_id)
        self.assertTrue(domatch)

    @patch.dict('xivo_cti.innerdata.config', auth=_auth_config)
    @patch('xivo_cti.innerdata.user_dao.get')
    @patch('xivo_cti.innerdata.AuthClient')
    def test_user_new_auth_token(self, auth_client_factory, get_user):
        user_id = 12
        auth_client = auth_client_factory.return_value
        auth_client.token.new.return_value = {'token': 'new-token'}
        get_user.return_value = Mock(username='my-login', password='my-password')

        result = self.safe.user_new_auth_token(user_id)

        auth_client_factory.assert_called_once_with(username='my-login',
                                                    password='my-password',
                                                    host='auth-host',
                                                    port=4242)
        auth_client.token.new.assert_called_once_with('xivo_user', expiration=TWO_MONTHS)
        self.assertEquals(result, 'new-token')

    @patch.dict('xivo_cti.innerdata.config', auth=_auth_config)
    @patch('xivo_cti.innerdata.user_dao.get')
    @patch('xivo_cti.innerdata.AuthClient')
    def test_user_remove_auth_token(self, auth_client_factory, get_user):
        user_id = 12
        auth_client = auth_client_factory.return_value

        self.safe.user_remove_auth_token(user_id, sentinel.token)

        auth_client_factory.assert_called_once_with(username=ANY,
                                                    password=ANY,
                                                    host='auth-host',
                                                    port=4242)
        auth_client.token.revoke.assert_called_once_with(sentinel.token)
