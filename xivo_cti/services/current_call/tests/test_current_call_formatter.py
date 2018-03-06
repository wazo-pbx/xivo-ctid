# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
import time

from mock import Mock

from xivo_cti.services.current_call import formatter
from xivo_cti.services.current_call import manager
from xivo_cti.services.current_call.manager import PEER_CHANNEL
from xivo_cti.services.current_call.manager import BRIDGE_TIME
from xivo_cti.services.current_call.manager import ON_HOLD
from xivo_cti import dao
from xivo_cti.dao.channel_dao import ChannelDAO


class TestCurrentCallFormatter(unittest.TestCase):

    def setUp(self):
        self.manager = Mock(manager.CurrentCallManager)
        self.formatter = formatter.CurrentCallFormatter()
        self.formatter._current_call_manager = self.manager
        self.line_identity_1 = 'SCCP/7890'
        self.line_identity_2 = 'SIP/abcd'
        now = time.time()
        self.channel_1 = {'id': 'SIP/abcdef-123456',
                          'cid_name': 'Alice',
                          'cid_number': '1234',
                          'start': now,
                          'holded': False}
        self.channel_2 = {'id': 'SCCP/1234-123456',
                          'cid_name': 'Bob',
                          'cid_number': '555',
                          'start': now,
                          'holded': True}

        self._state = {
            self.line_identity_1: [
                {PEER_CHANNEL: self.channel_1['id'],
                 BRIDGE_TIME: self.channel_1['start'],
                 ON_HOLD: self.channel_1['holded']}
            ],
            self.line_identity_2: [
                {PEER_CHANNEL: 'SCCP/7890-123556',
                 ON_HOLD: False},
                {PEER_CHANNEL: 'DAHDI/i1/543543-343545',
                 BRIDGE_TIME: now - 20,
                 ON_HOLD: True}
            ]
        }
        dao.channel = Mock(ChannelDAO)

    def test_get_line_current_call(self):
        formatted_call_1 = {'first': 'call'}
        self.formatter._format_call = Mock()
        self.formatter._format_call.return_value = formatted_call_1
        self.manager.get_line_calls.return_value = self._state[self.line_identity_1]

        formatted_current_call = self.formatter.get_line_current_call(self.line_identity_1)

        expected_current_call = {
            'class': 'current_calls',
            'current_calls': [
                formatted_call_1
            ]
        }

        self.assertEqual(formatted_current_call, expected_current_call)

    def test_get_line_current_call_unknown_channel(self):
        self.formatter._format_call = Mock()
        self.formatter._format_call.side_effect = LookupError()
        self.manager.get_line_calls.return_value = self._state[self.line_identity_1]

        formatted_current_call = self.formatter.get_line_current_call(self.line_identity_1)

        expected_current_call = {
            'class': 'current_calls',
            'current_calls': [
            ]
        }

        self.assertEqual(formatted_current_call, expected_current_call)

    def test_get_line_current_call_no_state_for_line(self):
        self.manager.get_line_calls.return_value = []

        formatted_current_call = self.formatter.get_line_current_call('SIP/nothere')

        expected_current_call = {
            'class': 'current_calls',
            'current_calls': [
            ]
        }

        self.assertEqual(formatted_current_call, expected_current_call)

    def test_format_call(self):
        call = {PEER_CHANNEL: self.channel_1['id'],
                BRIDGE_TIME: self.channel_1['start'],
                ON_HOLD: self.channel_1['holded']}

        dao.channel = Mock(ChannelDAO)
        dao.channel.get_caller_id_name_number.return_value = self.channel_1['cid_name'], self.channel_1['cid_number']

        result = self.formatter._format_call(call)

        expected = {'cid_name': self.channel_1['cid_name'],
                    'cid_number': self.channel_1['cid_number'],
                    'call_status': 'up',
                    'call_start': self.channel_1['start']}

        self.assertEqual(result, expected)

    def test_format_call_on_hold(self):
        call = {PEER_CHANNEL: self.channel_2['id'],
                BRIDGE_TIME: self.channel_2['start'],
                ON_HOLD: self.channel_2['holded']}

        dao.channel = Mock(ChannelDAO)
        dao.channel.get_caller_id_name_number.return_value = self.channel_2['cid_name'], self.channel_2['cid_number']

        result = self.formatter._format_call(call)

        expected = {'cid_name': self.channel_2['cid_name'],
                    'cid_number': self.channel_2['cid_number'],
                    'call_status': 'hold',
                    'call_start': self.channel_2['start']}

        self.assertEqual(result, expected)

    def test_attended_transfer_answered(self):
        line_identity = 'sip/sip_peer'
        expected = {'class': 'current_call_attended_transfer_answered',
                    'line': line_identity}

        result = self.formatter.attended_transfer_answered(line_identity)

        self.assertEqual(result, expected)
