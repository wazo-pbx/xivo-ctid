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

from hamcrest import assert_that, has_key, equal_to
from mock import Mock, call
from xivo_cti.channel import Channel
from xivo_cti.innerdata import Safe
from xivo_cti.services.bridge.bridge import Bridge
from xivo_cti.services.bridge.manager import BridgeManager
from xivo_cti.services.bridge.notifier import BridgeNotifier


class TestBridgeManager(unittest.TestCase):

    def setUp(self):
        self.bridge_id = 'e136cd36-5187-430c-af2a-d1f08870847b'
        self.bridge_type = 'basic'
        self.channel_name = 'SIP/foo-123'
        self.channel = Mock(Channel)
        self.bridge_notifier = Mock(BridgeNotifier)
        self.innerdata = Mock(Safe)
        self.innerdata.channels = {}
        self.bridge_manager = BridgeManager(self.bridge_notifier, self.innerdata)

    def _install_bridge(self):
        bridge = Mock(Bridge)
        self.bridge_manager._bridges[self.bridge_id] = bridge
        return bridge

    def test_on_bridge_create(self):
        self.bridge_manager._on_bridge_create(self.bridge_id, self.bridge_type)

        assert_that(self.bridge_manager._bridges, has_key(self.bridge_id))

    def test_on_bridge_destroy(self):
        self.bridge_manager._on_bridge_create(self.bridge_id, self.bridge_type)
        self.bridge_manager._on_bridge_destroy(self.bridge_id)

        assert_that(self.bridge_manager._bridges, equal_to({}))

    def test_on_bridge_enter(self):
        bridge = self._install_bridge()
        self.innerdata.channels[self.channel_name] = self.channel

        self.bridge_manager._on_bridge_enter(self.bridge_id, self.channel_name)

        bridge._add_channel.assert_called_once_with(self.channel)
        self.bridge_notifier._on_bridge_enter.assert_called_once_with(bridge, self.channel, bridge.linked.return_value)

    def test_on_bridge_leave(self):
        bridge = self._install_bridge()
        bridge.linked.side_effect = [False, False]
        self.innerdata.channels[self.channel_name] = self.channel

        self.bridge_manager._on_bridge_leave(self.bridge_id, self.channel_name)

        bridge._remove_channel.assert_called_once_with(self.channel)
        self.bridge_notifier._on_bridge_leave.assert_called_once_with(bridge, self.channel, False)

    def test_on_bridge_leave_unlinked(self):
        bridge = self._install_bridge()
        bridge.linked.side_effect = [True, False]
        self.innerdata.channels[self.channel_name] = self.channel

        self.bridge_manager._on_bridge_leave(self.bridge_id, self.channel_name)

        self.bridge_notifier._on_bridge_leave.assert_called_once_with(bridge, self.channel, True)

    def test_add_bridge(self):
        self.bridge_manager._add_bridge(self.bridge_id, self.bridge_type)

        assert_that(self.bridge_manager._bridges, has_key(self.bridge_id))

    def test_add_channel_to_bridge(self):
        bridge = self._install_bridge()
        self.innerdata.channels[self.channel_name] = self.channel

        self.bridge_manager._add_channel_to_bridge(self.bridge_id, self.channel_name)

        bridge._add_channel.assert_called_once_with(self.channel)
        assert_that(self.bridge_notifier._on_bridge_enter.called, equal_to(False))

    def test_finish_bridge_initialization(self):
        channel_1 = Mock()
        channel_2 = Mock()
        bridge = self._install_bridge()
        bridge.linked.return_value = True
        bridge.channels = [channel_1, channel_2]

        self.bridge_manager._finish_bridge_initialization(self.bridge_id)

        expected_calls = [
            call(channel_1.channel, channel_2.channel),
            call(channel_2.channel, channel_1.channel),
        ]
        assert_that(expected_calls, equal_to(self.innerdata.setpeerchannel.call_args_list))
