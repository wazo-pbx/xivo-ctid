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
from mock import Mock
from hamcrest import *

from xivo_cti.services.current_call import formatter
from xivo_cti.services.current_call import manager
from xivo_cti.services.current_call import notifier
from xivo_cti import xivo_ami


class TestCurrentCallManager(unittest.TestCase):

    def setUp(self):
        self.notifier = Mock(notifier.CurrentCallNotifier)
        self.formatter = Mock(formatter.CurrentCallFormatter)
        self.ami_class = Mock(xivo_ami.AMIClass)
        self.manager = manager.CurrentCallManager(self.notifier, self.formatter)
        self.manager.ami = self.ami_class
        self.line_1 = 'sip/tc8nb4'
        self.line_2 = 'sip/6s7foq'
        self.channel_1 = 'SIP/tc8nb4-00000004'
        self.channel_2 = 'SIP/6s7foq-00000005'

    @patch('time.time')
    def test_bridge_channels(self, mock_time):
        bridge_time = time.time()
        mock_time.return_value = bridge_time

        self.manager.bridge_channels(self.channel_1, self.channel_2)

        expected = {
            self.line_1: [
                {'channel': self.channel_2,
                 'lines_channel': self.channel_1,
                 'bridge_time': bridge_time,
                 'on_hold': False}
            ],
            self.line_2: [
                {'channel': self.channel_1,
                 'lines_channel': self.channel_2,
                 'bridge_time': bridge_time,
                 'on_hold': False}
            ],
        }

        self.assertEqual(self.manager._lines, expected)
        calls = self._get_notifier_calls()
        assert_that(calls, only_contains(self.line_1, self.line_2))

    def test_masquerade_channel(self):
        local_channel = 'Local/1002@pcm-dev-00000001;2'
        local_channel_iface = 'Local/1002@pcm-dev'
        bridge_time = 12345.65

        self.manager._lines = {
            self.line_1: [
                {'channel': local_channel,
                 'lines_channel': self.channel_1,
                 'bridge_time': bridge_time,
                 'on_hold': False},
            ],
            local_channel_iface: [
                {'channel': self.channel_1,
                 'lines_channel': local_channel,
                 'bridge_time': bridge_time,
                 'on_hold': False},
            ]
        }

        self.manager.masquerade(local_channel, self.channel_2)

        expected = {
            self.line_1: [
                {'channel': self.channel_2,
                 'lines_channel': self.channel_1,
                 'bridge_time': bridge_time,
                 'on_hold': False}
            ],
            self.line_2: [
                {'channel': self.channel_1,
                 'lines_channel': self.channel_2,
                 'bridge_time': bridge_time,
                 'on_hold': False}
            ],
        }

        self.assertEqual(self.manager._lines, expected)
        calls = self._get_notifier_calls()
        assert_that(calls, only_contains(self.line_1, self.line_2, local_channel_iface))

    def test_bridge_channels_on_hold(self):
        bridge_time = 123456.44

        self.manager._lines = {
            self.line_1: [
                {'channel': self.channel_2,
                 'bridge_time': bridge_time,
                 'on_hold': True}
            ],
            self.line_2: [
                {'channel': self.channel_1,
                 'bridge_time': bridge_time,
                 'on_hold': False}
            ],
        }

        self.manager.bridge_channels(self.channel_1, self.channel_2)

        expected = {
            self.line_1: [
                {'channel': self.channel_2,
                 'bridge_time': bridge_time,
                 'on_hold': True}
            ],
            self.line_2: [
                {'channel': self.channel_1,
                 'bridge_time': bridge_time,
                 'on_hold': False}
            ],
        }

        self.assertEqual(self.manager._lines, expected)
        self.assertEqual(self.notifier.publish_current_call.call_count, 0)

    def test_end_call(self):
        bridge_time = 123456.44

        self.manager._lines = {
            self.line_1: [
                {'channel': 'SIP/mytrunk-12345',
                 'lines_channel': 'SIP/tc8nb4-000002',
                 'bridge_time': bridge_time,
                 'on_hold': True},
                {'channel': self.channel_2,
                 'lines_channel': self.channel_1,
                 'bridge_time': bridge_time,
                 'on_hold': False},
            ],
            self.line_2: [
                {'channel': self.channel_1,
                 'lines_channel': self.channel_2,
                 'bridge_time': bridge_time,
                 'on_hold': False}
            ],
        }

        self.manager.end_call(self.channel_1)

        expected = {
            self.line_1: [
                {'channel': 'SIP/mytrunk-12345',
                 'lines_channel': 'SIP/tc8nb4-000002',
                 'bridge_time': bridge_time,
                 'on_hold': True}
            ],
        }

        self.assertEqual(self.manager._lines, expected)
        calls = self._get_notifier_calls()
        assert_that(calls, only_contains(self.line_1, self.line_2))

    def test_hold_channel(self):
        self.manager._lines = {
            self.line_1: [
                {'channel': self.channel_2,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
            self.line_2: [
                {'channel': self.channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        self.manager.hold_channel(self.channel_2)

        expected = {
            self.line_1: [
                {'channel': self.channel_2,
                 'bridge_time': 1234,
                 'on_hold': True}
            ],
            self.line_2: [
                {'channel': self.channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        self.assertEqual(self.manager._lines, expected)
        self.notifier.publish_current_call.assert_called_once_with(self.line_1)

    def test_unhold_channel(self):
        self.manager._lines = {
            self.line_1: [
                {'channel': self.channel_2,
                 'bridge_time': 1234,
                 'on_hold': True}
            ],
            self.line_2: [
                {'channel': self.channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        self.manager.unhold_channel(self.channel_2)

        expected = {
            self.line_1: [
                {'channel': self.channel_2,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
            self.line_2: [
                {'channel': self.channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        self.assertEqual(self.manager._lines, expected)
        self.notifier.publish_current_call.assert_called_once_with(self.line_1)

    def test_get_line_calls(self):
        self.manager._lines = {
            self.line_1: [
                {'channel': self.channel_2,
                 'bridge_time': 1234,
                 'on_hold': True}
            ],
            self.line_2: [
                {'channel': self.channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        calls = self.manager.get_line_calls(self.line_1)

        self.assertEquals(calls, self.manager._lines[self.line_1])

    def test_get_line_calls_no_line(self):
        channel_1 = 'SIP/tc8nb4-00000004'
        channel_2 = 'SIP/6s7foq-00000005'
        self.manager._lines = {
            self.line_1: [
                {'channel': channel_2,
                 'bridge_time': 1234,
                 'on_hold': True}
            ],
            self.line_2: [
                {'channel': channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        calls = self.manager.get_line_calls('SCCP/654')

        self.assertEquals(calls, [])

    def test_line_identity_from_channel(self):
        result = self.manager._identity_from_channel(self.channel_1)

        self.assertEqual(result, self.line_1)

    def _get_notifier_calls(self):
        return [call[0][0] for call in self.notifier.publish_current_call.call_args_list]

    @patch('xivo_dao.userfeatures_dao.get_line_identity')
    def test_hangup(self, mock_get_line_identity):
        user_id = 5
        self.manager._lines = {
            self.line_1: [
                {'channel': self.channel_2,
                 'lines_channel': self.channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
            self.line_2: [
                {'channel': self.channel_1,
                 'lines_channel': self.channel_2,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }
        mock_get_line_identity.return_value = self.line_1

        self.manager.hangup(user_id)

        self.ami_class.sendcommand.assert_called_once_with('Hangup', [('Channel', self.channel_1)])

    @patch('xivo_dao.userfeatures_dao.get_line_identity')
    def test_hangup_no_line(self, mock_get_line_identity):
        user_id = 5
        mock_get_line_identity.side_effect = LookupError()

        self.manager.hangup(user_id)

        self.assertEqual(self.ami_class.sendcommand.call_count, 0)
