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
from xivo_cti.call_forms.dispatch_filter import DispatchFilter
from xivo_cti.innerdata import Safe
from xivo_cti.services.bridge.manager import BridgeManager
from xivo_cti.services.bridge.updater import BridgeUpdater
from xivo_cti.services.call.receiver import CallReceiver
from xivo_cti.services.call.storage import CallStorage
from xivo_cti.services.current_call.manager import CurrentCallManager
from xivo_cti.xivo_ami import AMIClass


class TestBridgeUpdater(unittest.TestCase):

    def setUp(self):
        self.ami_class = Mock(AMIClass)
        self.bridge_manager = MagicMock(BridgeManager)
        self.call_receiver = Mock(CallReceiver)
        self.call_storage = Mock(CallStorage)
        self.current_call_manager = Mock(CurrentCallManager)
        self.dispatch_filter = Mock(DispatchFilter)
        self.innerdata = Mock(Safe)
        self.bridge_updater = BridgeUpdater(self.ami_class,
                                            self.bridge_manager,
                                            self.call_receiver,
                                            self.call_storage,
                                            self.current_call_manager,
                                            self.dispatch_filter,
                                            self.innerdata)

    def test_on_ami_bridge_create(self):
        ami_event = {'BridgeUniqueid': 'e136cd36-5187-430c-af2a-d1f08870847b',
                     'BridgeType': 'basic'}
        bridge_id = ami_event['BridgeUniqueid']
        bridge_type = ami_event['BridgeType']
        self.bridge_updater.on_ami_bridge_create(ami_event)
        self.bridge_manager._add_bridge.assert_called_once_with(bridge_id, bridge_type)

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
