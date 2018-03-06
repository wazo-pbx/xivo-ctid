# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, sentinel

from xivo_cti.services.current_call import parser
from xivo_cti.services.current_call import manager


class TestCurrentCallParser(unittest.TestCase):

    def setUp(self):
        self.manager = Mock(manager.CurrentCallManager)
        self.parser = parser.CurrentCallParser(self.manager)

    def test_that_bridge_leave_with_channels_remaining_in_the_bridge_does_nothing(self):
        event = {u'BridgeNumChannels': u'1',
                 u'Channel': sentinel.channel,
                 u'Event': u'BridgeLeave'}

        self.parser.parse_bridge_leave(event)

        self.assertEqual(self.manager.end_call.call_count, 0,
                         'end_call should not be called when a channel is left in the bridge')

    def test_that_bridge_leave_with_no_channels_left_calls_end_call(self):
        event = {u'BridgeNumChannels': u'0',
                 u'Channel': sentinel.channel,
                 u'Event': u'BridgeLeave'}

        self.parser.parse_bridge_leave(event)

        self.manager.end_call.assert_called_once_with(sentinel.channel)

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

    def test_parse_unhold(self):
        channel = 'SIP/nkvo55-00000003'
        unhold_event = {
            'Event': 'Unhold',
            'Privilege': 'call,all',
            'Channel': channel,
            'Uniqueid': 1354638961.3
        }

        self.parser.parse_unhold(unhold_event)

        self.assertEqual(self.manager.hold_channel.call_count, 0)
        self.manager.unhold_channel.assert_called_once_with(channel)

    def test_parse_hold(self):
        channel = 'SIP/nkvo55-00000003'
        hold_event = {
            'Event': 'Hold',
            'Privilege': 'call,all',
            'Channel': channel,
            'Uniqueid': 1354638961.3
        }

        self.parser.parse_hold(hold_event)

        self.manager.hold_channel.assert_called_once_with(channel)
        self.assertEqual(self.manager.unhold_channel.call_count, 0)

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
