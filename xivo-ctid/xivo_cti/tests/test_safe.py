# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
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
from xivo_cti.innerdata import Safe, Channel
from xivo_cti.context import context
from xivo_cti.cti.commands.getlists.list_id import ListID
from xivo_cti.cti.commands.getlists.update_config import UpdateConfig
from xivo_cti.cti.commands.getlists.update_status import UpdateStatus
from xivo_cti.cti.commands.directory import Directory
from xivo_cti.tools.weak_method import WeakCallable
from xivo_cti import cti_config
from xivo_cti import innerdata
from tests.mock import Mock
from xivo_cti.services.user_service_manager import UserServiceManager
from xivo_cti.cti.commands.availstate import Availstate
from xivo_dao.trunkfeaturesdao import TrunkFeaturesDAO


class TestSafe(unittest.TestCase):

    _ipbx_id = 'xivo'

    def setUp(self):
        context.register('config', cti_config.Config())
        self._ctiserver = CTIServer()
        self._ctiserver._init_db_connection_pool()
        self._ctiserver._user_service_manager = Mock(UserServiceManager)
        config = context.get('config')
        config.xc_json = {'ipbx': {'db_uri': 'sqlite://'}}
        self.safe = Safe(self._ctiserver, self._ipbx_id)
        self.safe.trunk_features_dao = Mock(TrunkFeaturesDAO)
        self.safe.trunk_features_dao.get_ids.return_value = []
        self.safe.init_status()

    def tearDown(self):
        pass

    def test_safe(self):
        self.assertEqual(self.safe._ctiserver, self._ctiserver)

    def test_register_cti_handlers(self):
        self.safe.register_cti_handlers()

        self.assert_callback_registered(ListID, self.safe.handle_getlist_list_id)
        self.assert_callback_registered(UpdateConfig, self.safe.handle_getlist_update_config)
        self.assert_callback_registered(UpdateStatus, self.safe.handle_getlist_update_status)
        self.assert_callback_registered(Directory, self.safe.getcustomers)
        self.assert_callback_registered(Availstate, self.safe._ctiserver._user_service_manager.set_presence)

    def test_handle_getlist_list_id_not_a_list(self):
        ret = self.safe.handle_getlist_list_id('not_a_list', '1')

        self.assertEqual(ret, None)

    def test_handle_getlist_list_id_queuemembers(self):
        self.safe.queuemembers_config['1'] = {}
        self.safe.queuemembers_config['2'] = {}
        expected_result = ('message', {'function': 'listid',
                                       'listname': 'queuemembers',
                                       'tipbxid': self._ipbx_id,
                                       'list': ['1', '2'],
                                       'class': 'getlist'})

        ret = self.safe.handle_getlist_list_id('queuemembers', 'someone')

        self.assertEqual(ret, expected_result)

    def test_split_channel(self):
        sip_trunk_channel = 'SIP/test-ha-1-03745898564'

        proto, name = innerdata.split_channel(sip_trunk_channel)

        self.assertEqual(proto, 'SIP')
        self.assertEqual(name, 'test-ha-1')

    def test_split_channel_local(self):
        sip_trunk_channel = 'Local/1105@default-3d0f;2'

        proto, name = innerdata.split_channel(sip_trunk_channel)

        self.assertEqual(proto, 'Local')
        self.assertEqual(name, '1105@default')

    def test_split_channel_dahdi(self):
        dahdi_trunk_channel = 'DAHDI/i1/0612345678-577'

        proto, name = innerdata.split_channel(dahdi_trunk_channel)

        self.assertEqual(proto, 'custom')
        self.assertEqual(name, 'DAHDI/i1')

    def assert_callback_registered(self, cls, fn):
        found = False
        for callback in cls._callbacks_with_params:
            if WeakCallable(fn) == callback[0]:
                found = True
        self.assertTrue(found, 'Could not find callback to function %s' % fn)

    def test_trunk_hangup(self):
        channel_name = 'SIP/mon_trunk-12345'

        channel = Mock(Channel)
        channel.relations = ['trunk:1']
        self.safe.channels[channel_name] = channel
        self.safe.xod_status['trunks'][1] = {'channels': [channel_name]}

        self.safe.hangup(channel_name)

        self.assertTrue(channel_name not in self.safe.channels)
        self.assertTrue(channel_name not in self.safe.xod_status['trunks'][1]['channels'])

    def test_init_status(self):
        id_list = [1, 2, 3, 4]
        safe = Safe(self._ctiserver, self._ipbx_id)
        safe.trunk_features_dao = Mock(TrunkFeaturesDAO)
        safe.trunk_features_dao.get_ids.return_value = id_list

        safe.init_status()

        self.assertTrue('trunks' in safe.xod_status)
        for trunk_id in id_list:
            self.assertTrue(trunk_id in safe.xod_status['trunks'])
            self.assertEqual(safe.xod_status['trunks'][trunk_id], safe.props_status['trunks'])
            self.assertFalse(safe.xod_status['trunks'][trunk_id] is safe.props_status['trunks'])


class TestChannel(unittest.TestCase):

    def test_has_extra_data(self):
        channel = Channel('local/1002@statcenter', 'statcenter', '1234.12')

        result = channel.has_extra_data('xivo', 'calleridname')

        self.assertFalse(result)

        channel.set_extra_data('xivo', 'calleridname', 'test')

        result = channel.has_extra_data('xivo', 'calleridname')

        self.assertTrue(result)

    def test_update_state(self):
        state = 'Ringing'

        channel = Channel('1001@my-ctx-00000', 'my-ctx', '1234567.33')

        channel.update_state(5, state)

        self.assertEqual(channel.state, 5)
        self.assertEqual(channel.properties['state'], state)
