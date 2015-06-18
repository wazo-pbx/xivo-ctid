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
from mock import Mock, MagicMock
from xivo_cti.services.bridge.manager import BridgeManager
from xivo_cti.services.bridge.updater import BridgeUpdater
from xivo_cti.xivo_ami import AMIClass
from xivo_cti.innerdata import Safe
from xivo_cti.call_forms.dispatch_filter import DispatchFilter


class TestBridgeUpdater(unittest.TestCase):

    def setUp(self):
        self.bridge_manager = MagicMock(BridgeManager)
        self.ami_class = Mock(AMIClass)
        self.innerdata = Mock(Safe)
        self.dispatch_filter = Mock(DispatchFilter)
        self.bridge_updater = BridgeUpdater(self.bridge_manager,
                                            self.ami_class,
                                            self.innerdata,
                                            self.dispatch_filter)

    def test_on_ami_bridge_create(self):
        ami_event = {'BridgeUniqueid': 'e136cd36-5187-430c-af2a-d1f08870847b'}
        bridge_id = ami_event['BridgeUniqueid']
        self.bridge_updater.on_ami_bridge_create(ami_event)
        self.bridge_manager._add_bridge.assert_called_once_with(bridge_id)

    def test_on_ami_bridge_destroy(self):
        ami_event = {'BridgeUniqueid': 'e136cd36-5187-430c-af2a-d1f08870847b'}
        bridge_id = ami_event['BridgeUniqueid']
        self.bridge_updater.on_ami_bridge_destroy(ami_event)
        self.bridge_manager._remove_bridge.assert_called_once_with(bridge_id)

    def test_on_ami_bridge_enter(self):
        pass

    def test_on_ami_bridge_leave(self):
        pass

    def test_on_ami_bridge_list_item(self):
        pass

    def test_on_ami_bridge_info_channel(self):
        pass

    def test_on_ami_bridge_info_complete(self):
        pass

    def test_update_channels(self):
        pass

    def test_update_peer_channels(self):
        pass
