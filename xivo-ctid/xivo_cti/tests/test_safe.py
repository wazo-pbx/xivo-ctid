# vim: set fileencoding=utf-8 :
# XiVO CTI Server

# Copyright (C) 2007-2011  Avencall'
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

import unittest

from xivo_cti.ctiserver import CTIServer
from xivo_cti.innerdata import Safe
from xivo_cti.cti_config import Config
from xivo_cti.cti.commands.getlists.list_id import ListID
from xivo_cti.cti.commands.getlists.update_config import UpdateConfig
from xivo_cti.cti.commands.getlists.update_status import UpdateStatus
from xivo_cti.cti.commands.directory import Directory
from xivo_cti.tools.weak_method import WeakCallable
from xivo_cti import innerdata
from tests.mock import Mock
from xivo_cti.tools.caller_id import build_agi_caller_id
from xivo_cti.services.user_service_manager import UserServiceManager
from xivo_cti.cti.commands.availstate import Availstate


class TestSafe(unittest.TestCase):

    _ipbx_id = 'xivo_test'

    def setUp(self):
        self._ctiserver = CTIServer()
        self._ctiserver._init_db_connection_pool()
        self._ctiserver._user_service_manager = Mock(UserServiceManager())
        config = Config.get_instance()
        config.xc_json = {'ipbxes': {self._ipbx_id: {'cdr_db_uri': 'sqlite://'}}}

    def tearDown(self):
        pass

    def test_safe(self):
        safe = Safe(self._ctiserver, self._ipbx_id)

        self.assertEqual(safe._ctiserver, self._ctiserver)
        self.assertEqual(safe.ipbxid, self._ipbx_id)

    def test_register_cti_handlers(self):
        safe = Safe(self._ctiserver, self._ipbx_id)

        safe.register_cti_handlers()

        self.assert_callback_registered(ListID, safe.handle_getlist_list_id)
        self.assert_callback_registered(UpdateConfig, safe.handle_getlist_update_config)
        self.assert_callback_registered(UpdateStatus, safe.handle_getlist_update_status)
        self.assert_callback_registered(Directory, safe.getcustomers)
        self.assert_callback_registered(Availstate, safe._ctiserver._user_service_manager.set_presence)

    def test_handle_getlist_list_id_not_a_list(self):
        safe = Safe(self._ctiserver, self._ipbx_id)

        ret = safe.handle_getlist_list_id('not_a_list', '1')

        self.assertEqual(ret, None)

    def test_handle_getlist_list_id_queuemembers(self):
        safe = Safe(self._ctiserver, self._ipbx_id)
        safe.queuemembers_config['1'] = {}
        safe.queuemembers_config['2'] = {}
        expected_result = ('message', {'function': 'listid',
                                       'listname': 'queuemembers',
                                       'tipbxid': self._ipbx_id,
                                       'list': ['1', '2'],
                                       'class': 'getlist'})

        ret = safe.handle_getlist_list_id('queuemembers', 'someone')

        self.assertEqual(ret, expected_result)

    def test_split_channel(self):
        sip_trunk_channel = 'SIP/test-ha-1-03745898564'

        proto, name = innerdata.split_channel(sip_trunk_channel)

        self.assertEqual(proto, 'SIP')
        self.assertEqual(name, 'test-ha-1')

    def test_resolve_incoming_caller_id_already_set(self):
        safe = Safe(self._ctiserver, self._ipbx_id)

        ret = safe._resolve_incoming_caller_id('SIP/test-123', 'Tester', '6666', None)

        self.assertEqual(ret, {})

    def test_resolve_incoming_caller_id_phone(self):
        safe = Safe(self._ctiserver, self._ipbx_id)

        channel_id = 'SIP/abcdef-1234'
        safe._get_cid_for_phone = Mock()
        safe._is_phone_channel = Mock()
        name = 'tester'
        number = '1234'
        full = '"%s" <%s>' % (name, number)
        safe._get_cid_for_phone.return_value = (full, name, number)
        safe._is_phone_channel.return_value = True

        expected = build_agi_caller_id(full, name, number)

        ret = safe._resolve_incoming_caller_id(channel_id, number, number, None)

        self.assertEqual(expected, ret)

    def test_resolve_incoming_caller_id_trunk(self):
        safe = Safe(self._ctiserver, self._ipbx_id)

        safe._is_phone_channel = Mock()
        safe._is_phone_channel.return_value = False
        safe._is_trunk_channel = Mock()
        safe._is_trunk_channel.return_value = True
        trunks = {1: {'name': 'my-test-trunk',
                      'protocol': 'sip',
                      'context': 'from-extern'}}
        safe.xod_config['trunks'].keeplist = trunks
        safe._get_cid_directory_lookup = Mock()
        channel_id = 'SIP/my-test-trunk-123456'
        name = 'tester'
        number = '666'
        full = '"%s" <%s>' % (name, number)
        safe._get_cid_directory_lookup.return_value = (full, name, number)

        expected = build_agi_caller_id(full, name, number)

        ret = safe._resolve_incoming_caller_id(channel_id, number, number, 1)

        self.assertEqual(ret, expected)

    def test_resolve_incoming_caller_id_queue_internal(self):
        safe = Safe(self._ctiserver, self._ipbx_id)
        channel = 'Local/1000@default-19e6;2'
        name = 'tester'
        number = '1234'

        ret = safe._resolve_incoming_caller_id(channel, name, number, None)

        self.assertEqual(ret, {})

    def test_resolve_incoming_caller_id_queue_trunk(self):
        safe = Safe(self._ctiserver, self._ipbx_id)
        channel = 'Local/1000@default-19e6;2'
        number = '1234'
        name = 'Tester'
        full = '"%s" <%s>' % (name, number)
        safe._get_cid_directory_lookup = Mock()
        safe._get_cid_directory_lookup.return_value = ('"%s" <%s>' % (name, number),
                                                       name, number)

        expected = build_agi_caller_id(full, name, number)

        ret = safe._resolve_incoming_caller_id(channel, number, number, None)

        self.assertEqual(ret, expected)

    def assert_callback_registered(self, cls, fn):
        found = False
        for callback in cls._callbacks_with_params:
            if WeakCallable(fn) == callback[0]:
                found = True
        self.assertTrue(found, 'Could not find callback to function %s' % fn)
