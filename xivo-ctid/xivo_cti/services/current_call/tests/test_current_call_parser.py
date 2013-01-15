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

from mock import Mock

from xivo_cti.services.current_call import parser
from xivo_cti.services.current_call import manager


class TestCurrentCallParser(unittest.TestCase):

    def setUp(self):
        self.manager = Mock(manager.CurrentCallManager)
        self.parser = parser.CurrentCallParser(self.manager)

    def test_parse_bridge(self):
        channel_1 = 'SIP/xivo-dev-00000002'
        channel_2 = 'SIP/nkvo55-00000003'
        bridge_event = {
            'Event': 'Bridge',
            'Privilege': 'call,all',
            'Bridgestate': 'Link',
            'Bridgetype': 'core',
            'Channel1': channel_1,
            'Channel2': channel_2,
            'Uniqueid1': 1354638961.2,
            'Uniqueid2': 1354638961.3,
            'CallerID1': '102',
            'CallerID2': '1001'
        }

        self.parser.parse_bridge(bridge_event)

        self.manager.bridge_channels.assert_called_once_with(channel_1, channel_2)

    def test_parse_hold_on(self):
        channel = 'SIP/nkvo55-00000003'
        hold_event = {
            'Event': 'Hold',
            'Privilege': 'call,all',
            'Status': 'On',
            'Channel': channel,
            'Uniqueid': 1354638961.3
        }

        self.parser.parse_hold(hold_event)

        self.manager.hold_channel.assert_called_once_with(channel)
        self.assertEqual(self.manager.unhold_channel.call_count, 0)

    def test_parse_hold_off(self):
        channel = 'SIP/nkvo55-00000003'
        hold_event = {
            'Event': 'Hold',
            'Privilege': 'call,all',
            'Status': 'Off',
            'Channel': channel,
            'Uniqueid': 1354638961.3
        }

        self.parser.parse_hold(hold_event)

        self.assertEqual(self.manager.hold_channel.call_count, 0)
        self.manager.unhold_channel.assert_called_once_with(channel)

    def test_parse_hangup(self):
        channel = 'SIP/tc8nb4-000000000038'
        hangup_event = {'Event': 'Hangup',
                        'Privilege': 'call,all',
                        'Channel': channel,
                        'Uniqueid': 1354737691.78,
                        'CallerIDNum': '1003',
                        'CallerIDName': 'Carlõs',
                        'ConnectedLineNum': '1002',
                        'ConnectedLineName': 'Bõb',
                        'Cause': '16',
                        'Cause-txt': 'Normal Clearing'}

        self.parser.parse_hangup(hangup_event)

        self.manager.end_call.assert_called_once_with(channel)

    def test_parse_hangup_transfer(self):
        channel = 'Local/102@default-00000028;1'
        hangup_event = {'Event': 'Hangup',
                        'Privilege': 'call,all',
                        'Channel': 'Local/102@default-00000028;1',
                        'Uniqueid': '1358264807.166',
                        'CallerIDNum': '102',
                        'CallerIDName': 'Bob',
                        'ConnectedLineNum': '101',
                        'ConnectedLineName': 'Alice Wunderland',
                        'Cause': '16',
                        'Cause-txt': 'Normal Clearing'}

        self.parser.parse_hangup(hangup_event)

        self.manager.remove_transfer_channel.assert_called_once_with(channel)

    def test_parse_masquerade(self):
        original_channel = 'Local/1002@pcm-dev-00000001;1',
        clone_channel = 'SIP/6s7foq-00000005',
        masquerade_event = {
            'Event': 'Masquerade',
            'Privilege': 'call,all',
            'Clone': clone_channel,
            'CloneState': 'Up',
            'Original': original_channel,
            'OriginalState': 'Up'
        }

        self.parser.parse_masquerade(masquerade_event)

        self.manager.masquerade.assert_called_once_with(
            original_channel, clone_channel
        )

    def test_parse_varset_transfername(self):
        channel = u'SIP/6s7foq-0000007b'
        transfer_channel = u'Local/1003@pcm-dev-00000021;1'
        varset_transfername_event = {
            'Event': 'VarSet',
            'Privilege': 'dialplan,all',
            'Channel': 'Local/1003@pcm-dev-00000021;1',
            'Variable': 'TRANSFERERNAME',
            'Value': 'SIP/6s7foq-0000007b',
            'Uniqueid': '1357921621.212',
        }

        self.parser.parse_varset_transfername(varset_transfername_event)

        self.manager.set_transfer_channel.assert_called_once_with(
            channel, transfer_channel
        )
