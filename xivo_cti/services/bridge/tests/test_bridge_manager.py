# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

from hamcrest import assert_that, equal_to, has_key, is_not, none
from xivo_cti.services.bridge.manager import BridgeManager


class BridgeManagerTest(unittest.TestCase):

    def setUp(self):
        self.bridge_manager = BridgeManager()

    def test_add_bridge(self):
        bridge_id = u'e136cd36-5187-430c-af2a-d1f08870847b'
        bridge_type = u'basic'
        self.bridge_manager._add_bridge(bridge_id, bridge_type)

        assert_that(self.bridge_manager._bridges, has_key(bridge_id))

    def test_remove_bridge(self):
        bridge_id = u'e136cd36-5187-430c-af2a-d1f08870847b'
        bridge_type = u'basic'
        self.bridge_manager._add_bridge(bridge_id, bridge_type)
        self.bridge_manager._remove_bridge(bridge_id)

        assert_that(self.bridge_manager._bridges, is_not(has_key(bridge_id)))

    def test_remove_bridge_non_existent(self):
        bridge_id = u'e136cd36-5187-430c-af2a-d1f08870847b'
        self.bridge_manager._remove_bridge(bridge_id)

        assert_that(self.bridge_manager._bridges, is_not(has_key(bridge_id)))

    def test_get_bridge(self):
        bridge_id = u'e136cd36-5187-430c-af2a-d1f08870847b'
        bridge_type = u'basic'
        self.bridge_manager._add_bridge(bridge_id, bridge_type)
        bridge = self.bridge_manager.get_bridge(bridge_id)

        assert_that(bridge.bridge_id, equal_to(bridge_id))

    def test_get_bridge_non_existent(self):
        bridge_id = u'e136cd36-5187-430c-af2a-d1f08870847b'
        bridge = self.bridge_manager.get_bridge(bridge_id)

        assert_that(bridge, none())
