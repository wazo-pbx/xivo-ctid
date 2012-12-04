# -*- coding: utf-8 -*-

import unittest
import time

from mock import Mock

from xivo_cti.services.current_call import formatter
from xivo_cti import dao
from xivo_cti.dao.channel_dao import ChannelDAO


class TestCurrentCallFormatter(unittest.TestCase):

    def setUp(self):
        self.formatter = formatter.CurrentCallFormatter()
        self.line_identity_1 = 'SCCP/7890'
        self.line_identity_2 = 'SIP/abcd'
        now = time.time()
        self.channel_1 = {'id': 'SIP/abcdef-123456',
                          'cid_name': 'Alice',
                          'cid_number': '1234',
                          'start': now,
                          'holded': False}
        self._state = {
            self.line_identity_1: [
                {'channel': self.channel_1['id'],
                 'bridge_time': self.channel_1['start'],
                 'on_hold': self.channel_1['holded']}
            ],
            self.line_identity_2: [
                {'channel': 'SCCP/7890-123556',
                 'brigde_time': now,
                 'on_hold': False},
                {'channel': 'DAHDI/i1/543543-343545',
                 'bridge_time': now - 20,
                 'on_hold': True}
            ]
        }
        dao.channel = Mock(ChannelDAO)

    def test_get_line_current_call(self):
        formatted_call_1 = {'first': 'call'}
        self.formatter._format_call = Mock()
        self.formatter._format_call.return_value = formatted_call_1
        self.formatter._state = self._state

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
        self.formatter._state = self._state

        formatted_current_call = self.formatter.get_line_current_call(self.line_identity_1)

        expected_current_call = {
            'class': 'current_calls',
            'current_calls': [
            ]
        }

        self.assertEqual(formatted_current_call, expected_current_call)

    def test_get_line_current_call_no_state_for_line(self):
        formatted_current_call = self.formatter.get_line_current_call('SIP/nothere')

        expected_current_call = {
            'class': 'current_calls',
            'current_calls': [
            ]
        }

        self.assertEqual(formatted_current_call, expected_current_call)

    def test_format_call(self):
        call = {'channel': self.channel_1['id'],
                'bridge_time': self.channel_1['start'],
                'on_hold': self.channel_1['holded']}

        dao.channel = Mock(ChannelDAO)
        dao.channel.get_caller_id_name_number.return_value = self.channel_1['cid_name'], self.channel_1['cid_number']

        result = self.formatter._format_call(call)

        expected = {'cid_name': self.channel_1['cid_name'],
                    'cid_number': self.channel_1['cid_number'],
                    'call_status': 'up',
                    'call_start': self.channel_1['start']}

        self.assertEqual(result, expected)
