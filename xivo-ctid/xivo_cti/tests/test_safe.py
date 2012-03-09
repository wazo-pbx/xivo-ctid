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


class TestSafe(unittest.TestCase):

    _ipbx_id = 'xivo_test'

    def setUp(self):
        self._ctiserver = CTIServer()
        self._ctiserver._init_db_connection_pool()
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

    def test_handle_getlist_listid(self):
        safe = Safe(self._ctiserver, self._ipbx_id)

        ret = safe.handle_getlist_list_id('not_a_list', '1')

        self.assertEqual(ret, None)

    def test_split_channel(self):
        sip_trunk_channel = 'SIP/test-ha-1-03745898564'

        proto, name = innerdata.split_channel(sip_trunk_channel)

        self.assertEqual(proto, 'SIP')
        self.assertEqual(name, 'test-ha-1')

    def assert_callback_registered(self, cls, fn):
        found = False
        for callback in cls._callbacks_with_params:
            if WeakCallable(fn) == callback[0]:
                found = True
        self.assertTrue(found, 'Could not find callback to function %s' % fn)
