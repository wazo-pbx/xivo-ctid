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
# contracted with Avencall. See the LICENSE file at top of the source tree
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
import time
from mock import patch

from xivo_cti.services.current_call import manager


class TestCurrentCallManager(unittest.TestCase):

    @patch('time.time')
    def test_bridge_channels(self, mock_time):
        line_1 = 'SIP/tc8nb4'
        line_2 = 'SIP/6s7foq'
        channel_1 = 'SIP/tc8nb4-00000004'
        channel_2 = 'SIP/6s7foq-00000005'
        bridge_time = time.time()
        mock_time.return_value = bridge_time
        current_call_manager = manager.CurrentCallManager()

        current_call_manager.bridge_channels(channel_1, channel_2)

        expected = {
            line_1: [
                {'channel': channel_2,
                 'bridge_time': bridge_time,
                 'on_hold': False}
            ],
            line_2: [
                {'channel': channel_1,
                 'bridge_time': bridge_time,
                 'on_hold': False}
            ],
        }

        self.assertEqual(current_call_manager._lines, expected)

    def test_hold_channel(self):
        line_1 = 'SIP/tc8nb4'
        line_2 = 'SIP/6s7foq'
        channel_1 = 'SIP/tc8nb4-00000004'
        channel_2 = 'SIP/6s7foq-00000005'
        current_call_manager = manager.CurrentCallManager()
        current_call_manager._lines = {
            line_1: [
                {'channel': channel_2,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
            line_2: [
                {'channel': channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        current_call_manager.hold_channel(channel_2)

        expected = {
            line_1: [
                {'channel': channel_2,
                 'bridge_time': 1234,
                 'on_hold': True}
            ],
            line_2: [
                {'channel': channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        self.assertEqual(current_call_manager._lines, expected)

    def test_unhold_channel(self):
        line_1 = 'SIP/tc8nb4'
        line_2 = 'SIP/6s7foq'
        channel_1 = 'SIP/tc8nb4-00000004'
        channel_2 = 'SIP/6s7foq-00000005'
        current_call_manager = manager.CurrentCallManager()
        current_call_manager._lines = {
            line_1: [
                {'channel': channel_2,
                 'bridge_time': 1234,
                 'on_hold': True}
            ],
            line_2: [
                {'channel': channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        current_call_manager.unhold_channel(channel_2)

        expected = {
            line_1: [
                {'channel': channel_2,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
            line_2: [
                {'channel': channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        self.assertEqual(current_call_manager._lines, expected)

    def test_unbridge_channels(self):
        line_1 = 'SIP/tc8nb4'
        line_2 = 'SIP/6s7foq'
        channel_1 = 'SIP/tc8nb4-00000004'
        channel_2 = 'SIP/6s7foq-00000005'
        current_call_manager = manager.CurrentCallManager()
        current_call_manager._lines = {
            line_1: [
                {'channel': channel_2,
                 'bridge_time': 1234,
                 'on_hold': True}
            ],
            line_2: [
                {'channel': channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        current_call_manager.unbridge_channels(channel_1, channel_2)

        expected = {
        }

        self.assertEqual(current_call_manager._lines, expected)

    def test_get_line_calls(self):
        line_1 = 'SIP/tc8nb4'
        line_2 = 'SIP/6s7foq'
        channel_1 = 'SIP/tc8nb4-00000004'
        channel_2 = 'SIP/6s7foq-00000005'
        current_call_manager = manager.CurrentCallManager()
        current_call_manager._lines = {
            line_1: [
                {'channel': channel_2,
                 'bridge_time': 1234,
                 'on_hold': True}
            ],
            line_2: [
                {'channel': channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        calls = current_call_manager.get_line_calls(line_1)

        self.assertEquals(calls, current_call_manager._lines[line_1])

    def test_get_line_calls_no_line(self):
        line_1 = 'SIP/tc8nb4'
        line_2 = 'SIP/6s7foq'
        channel_1 = 'SIP/tc8nb4-00000004'
        channel_2 = 'SIP/6s7foq-00000005'
        current_call_manager = manager.CurrentCallManager()
        current_call_manager._lines = {
            line_1: [
                {'channel': channel_2,
                 'bridge_time': 1234,
                 'on_hold': True}
            ],
            line_2: [
                {'channel': channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        calls = current_call_manager.get_line_calls('SCCP/654')

        self.assertEquals(calls, [])

    def test_line_identity_from_channel(self):
        channel = 'SIP/abcd-12345'
        line = 'SIP/abcd'

        current_call_manager = manager.CurrentCallManager()

        result = current_call_manager._identity_from_channel(channel)

        self.assertEqual(result, line)
