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
from mock import Mock
from xivo_cti.call_forms.dispatch_filter import DispatchFilter
from xivo_cti.channel import Channel
from xivo_cti.innerdata import Safe
from xivo_cti.services.bridge.manager import BridgeManager
from xivo_cti.services.bridge.updater import BridgeUpdater
from xivo_cti.services.bridge.bridge import Bridge
from xivo_cti.services.call.receiver import CallReceiver
from xivo_cti.services.call.storage import CallStorage
from xivo_cti.services.current_call.manager import CurrentCallManager
from xivo_cti.xivo_ami import AMIClass


class TestBridgeUpdater(unittest.TestCase):

    def setUp(self):
        self.ami_class = Mock(AMIClass)
        self.bridge_manager = Mock(BridgeManager)
        self.call_receiver = Mock(CallReceiver)
        self.call_storage = Mock(CallStorage)
        self.current_call_manager = Mock(CurrentCallManager)
        self.call_form_dispatch_filter = Mock(DispatchFilter)
        self.innerdata = Mock(Safe)
        self.bridge_updater = BridgeUpdater(self.ami_class,
                                            self.bridge_manager,
                                            self.call_form_dispatch_filter,
                                            self.call_receiver,
                                            self.call_storage,
                                            self.current_call_manager,
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

    def test_that_on_ami_bridge_adds_channel(self):
        ami_event = {'BridgeUniqueid': 'e136cd36-5187-430c-af2a-d1f08870847b',
                     'Channel': 'SIP/n5ksoc-00000001'}
        channel_name = ami_event['Channel']

        bridge = Mock(Bridge)
        bridge.basic_channels_connected.return_value = False
        self.bridge_manager.get_bridge.return_value = bridge

        self.bridge_updater.on_ami_bridge_enter(ami_event)

        bridge.add_channel.assert_called_once_with(channel_name)

    def test_that_on_ami_bridge_propagates_information_when_multiple_channels_in_a_bridge(self):
        ami_event = {'BridgeUniqueid': 'e136cd36-5187-430c-af2a-d1f08870847c',
                     'Channel': 'SIP/n5ksoc-00000002'}

        channel_name_1 = 'SIP/n5ksoc-00000001'
        channel_name_2 = ami_event['Channel']

        bridge = Mock(Bridge)
        bridge.channels = [channel_name_1, channel_name_2]
        bridge.basic_channels_connected.return_value = True
        self.bridge_manager.get_bridge.return_value = bridge

        channel_1 = Mock(Channel)
        channel_1.channel = channel_name_1
        channel_1.unique_id = '023456789'
        channel_1.properties = {'commstatus': 'ready',
                                'timestamp': '123'}
        channel_2 = Mock(Channel)
        channel_2.channel = channel_name_2
        channel_2.unique_id = '123456789'
        channel_2.properties = {'commstatus': 'calling',
                                'timestamp': '123'}

        self.innerdata.channels = {channel_name_1: channel_1,
                                   channel_name_2: channel_2}

        self.bridge_updater.on_ami_bridge_enter(ami_event)

        self.call_form_dispatch_filter.handle_bridge.assert_called_once_with(channel_2.unique_id,
                                                                             channel_2.channel)
        self.innerdata.update.assert_any_call(channel_name_1)
        self.innerdata.update.assert_any_call(channel_name_2)
        self.innerdata.setpeerchannel.assert_any_call(channel_name_1, channel_name_2)
        self.innerdata.setpeerchannel.assert_any_call(channel_name_2, channel_name_1)

    def test_that_on_ami_bridge_does_nothing_when_only_one_channel_in_a_bridge(self):
        ami_event = {'BridgeUniqueid': 'e136cd36-5187-430c-af2a-d1f08870847b',
                     'Channel': 'SIP/n5ksoc-00000001'}

        bridge = Mock(Bridge)
        bridge.basic_channels_connected.return_value = False
        self.bridge_manager.get_bridge.return_value = bridge

        self.bridge_updater.on_ami_bridge_enter(ami_event)

        self.assertFalse(self.call_form_dispatch_filter.handle_bridge.called)
        self.assertFalse(self.innerdata.update.called)
        self.assertFalse(self.innerdata.setpeerchannel.called)

    def test_that_on_ami_bridge_leave_removes_channel(self):
        ami_event = {'BridgeUniqueid': 'e136cd36-5187-430c-af2a-d1f08870847b',
                     'BridgeNumChannels': 0,
                     'Channel': 'SIP/n5ksoc-00000001',
                     'Uniqueid': '123456789'}
        channel_name = ami_event['Channel']

        bridge = Mock(Bridge)
        self.bridge_manager.get_bridge.return_value = bridge

        self.bridge_updater.on_ami_bridge_leave(ami_event)

        bridge.remove_channel.assert_called_once_with(channel_name)

    def test_that_on_ami_bridge_leave_calls_end_call_when_bridgenumchannels_is_lower_than_two(self):
        ami_event = {'BridgeUniqueid': 'e136cd36-5187-430c-af2a-d1f08870847b',
                     'BridgeNumChannels': 1,
                     'Channel': 'SIP/n5ksoc-00000001',
                     'Uniqueid': '123456789'}
        unique_id = ami_event['Uniqueid']

        bridge = Mock(Bridge)
        self.bridge_manager.get_bridge.return_value = bridge

        self.bridge_updater.on_ami_bridge_leave(ami_event)

        self.call_storage.end_call.assert_called_once_with(unique_id)

    def test_that_on_ami_bridge_leave_does_nothing_when_bridgenumchannels_is_bigger_than_one(self):
        ami_event = {'BridgeUniqueid': 'e136cd36-5187-430c-af2a-d1f08870847b',
                     'BridgeNumChannels': 2,
                     'Channel': 'SIP/n5ksoc-00000001',
                     'Uniqueid': '123456789'}

        bridge = Mock(Bridge)
        self.bridge_manager.get_bridge.return_value = bridge

        self.bridge_updater.on_ami_bridge_leave(ami_event)

        self.assertFalse(self.call_storage.end_call.called)

    def test_on_ami_bridge_list_item(self):
        ami_event = {'BridgeUniqueid': 'e136cd36-5187-430c-af2a-d1f08870847b',
                     'BridgeType': 'basic'}
        bridge_id = ami_event['BridgeUniqueid']
        self.bridge_updater.on_ami_bridge_list_item(ami_event)
        self.ami_class.sendcommand.assert_called_once_with('BridgeInfo', [('BridgeUniqueid', bridge_id)])

    def test_on_ami_bridge_info_channel(self):
        ami_event = {'ActionID': 'e136cd36-5187-430c-af2a-d1f08870847b',
                     'Channel': 'SIP/n5ksoc-0000001b'}
        channel = ami_event['Channel']

        bridge = Mock(Bridge)
        self.bridge_manager.get_bridge.return_value = bridge

        self.bridge_updater.on_ami_bridge_info_channel(ami_event)

        bridge.add_channel.assert_called_once_with(channel)

    def test_on_ami_bridge_info_complete(self):
        ami_event = {'BridgeUniqueid': 'e136cd36-5187-430c-af2a-d1f08870847b'}
        channel_name_1 = 'SIP/n5ksoc-00000001'
        channel_name_2 = 'SIP/n5ksoc-00000002'

        bridge = Mock(Bridge)
        bridge.channels = [channel_name_1, channel_name_2]
        bridge.basic_channels_connected.return_value = True
        self.bridge_manager.get_bridge.return_value = bridge

        self.bridge_updater.on_ami_bridge_info_complete(ami_event)

        self.innerdata.setpeerchannel.assert_any_call(channel_name_1, channel_name_2)
        self.innerdata.setpeerchannel.assert_any_call(channel_name_2, channel_name_1)
