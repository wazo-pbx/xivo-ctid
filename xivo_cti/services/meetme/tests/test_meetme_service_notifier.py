#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, patch
from xivo_cti.services.meetme.service_notifier import MeetmeServiceNotifier
from xivo_cti.services.meetme import encoder
from xivo_cti.interfaces.interface_cti import CTI


@patch('xivo_cti.services.meetme.service_notifier.config',
       {'main': {'context_separation': False}})
class TestMeetmeServiceNotifier(unittest.TestCase):

    def setUp(self):
        self.ipbx_id = 'xivo'
        self.notifier = MeetmeServiceNotifier()
        self.notifier.ipbx_id = self.ipbx_id

    @patch('xivo_dao.user_line_dao.get_line_identity_by_user_id')
    def test_subscribe_update(self, get_line_identity):
        user_id = 5
        channel_pattern = 'SIP/abcde'
        get_line_identity.return_value = channel_pattern

        client_connection = Mock(CTI)
        client_connection.user_id.return_value = user_id

        self.notifier._send_meetme_membership = Mock()
        self.notifier._current_state = {'800': {'number': '800',
                                                'name': 'test_conf',
                                                'pin_required': True,
                                                'start_time': 12345.123,
                                                'context': 'default',
                                                'members': {1: {'join_order': 1,
                                                                'join_time': 12345.123,
                                                                'number': '1002',
                                                                'name': 'Tester 1',
                                                                'channel': 'sip/bcde',
                                                                'muted': True}}}}

        expected_msg = encoder.encode_update(self.notifier._current_state)

        self.notifier.subscribe(client_connection)

        self.assertTrue(client_connection in self.notifier._subscriptions)

        expected_subscription = {'channel_start': channel_pattern,
                                 'membership': []}

        self.assertEqual(self.notifier._subscriptions[client_connection], expected_subscription)
        client_connection.send_message.assert_called_once_with(expected_msg)
        self.notifier._send_meetme_membership.assert_called_once_with()

    def test_publish_meetme_update(self):
        client_connection_1 = Mock(CTI)
        client_connection_2 = Mock(CTI)

        self.notifier._subscriptions = {client_connection_1: {'channel_start': 'sip/abcd',
                                                              'membership': []},
                                        client_connection_2: {'channel_start': 'sip/bcde',
                                                              'membership': []}}
        msg = {'800': {'number': '800',
                       'name': 'test_conf',
                       'pin_required': True,
                       'start_time': 12345.123,
                       'context': 'default',
                       'members': {1: {'join_order': 1,
                                       'join_time': 12345.123,
                                       'number': '1002',
                                       'name': 'Tester 1',
                                       'channel': 'sip/bcde',
                                       'muted': True}}}}

        expected_msg = encoder.encode_update(msg)
        self.notifier._send_meetme_membership = Mock()

        self.notifier.publish_meetme_update(msg)

        client_connection_1.send_message.assert_called_once_with(expected_msg)
        client_connection_2.send_message.assert_called_once_with(expected_msg)

    def test_publish_no_change(self):
        client_connection_1 = Mock(CTI)
        client_connection_2 = Mock(CTI)

        self.notifier._subscriptions = {client_connection_1: {'channel_start': 'sip/abcd',
                                                              'membership': []},
                                        client_connection_2: {'channel_start': 'sip/bcde',
                                                              'membership': []}}
        msg = {'800': {'number': '800',
                       'name': 'test_conf',
                       'pin_required': True,
                       'start_time': 12345.123,
                       'context': 'default',
                       'members': {1: {'join_order': 1,
                                       'join_time': 12345.123,
                                       'number': '1002',
                                       'name': 'Tester 1',
                                       'channel': 'sip/bcde',
                                       'muted': True}}}}

        self.notifier._current_state = msg

        self.notifier.publish_meetme_update(msg)

        self.assertFalse(client_connection_1.send_message.called)
        self.assertFalse(client_connection_2.send_message.called)

    def test_push_to_client_no_context_separation(self):
        client_connection = Mock(CTI)

        msg = {'800': {'number': '800',
                       'name': 'test_conf',
                       'pin_required': True,
                       'start_time': 12345.123,
                       'context': 'default',
                       'members': {1: {'join_order': 1,
                                       'join_time': 12345.123,
                                       'number': '1002',
                                       'name': 'Tester 1',
                                       'channel': 'sip/bcde',
                                       'muted': True}}},
               '801': {'number': '801',
                       'name': 'test_conf',
                       'pin_required': True,
                       'start_time': 12345.123,
                       'context': 'other',
                       'members': {1: {'join_order': 1,
                                       'join_time': 12345.123,
                                       'number': '1002',
                                       'name': 'Tester 1',
                                       'channel': 'sip/bcde',
                                       'muted': True}}}}

        expected = encoder.encode_update(msg)

        self.notifier._current_state = msg
        self.notifier._push_to_client(client_connection)

        client_connection.send_message.assert_called_once_with(expected)

    def test_send_membership_info(self):
        client_connection_1 = Mock(CTI)
        client_connection_2 = Mock(CTI)
        self.notifier._subscriptions = {client_connection_1: {'channel_start': 'sip/abcd',
                                                              'membership': []},
                                        client_connection_2: {'channel_start': 'sip/bcde',
                                                              'membership': []}}

        msg = {'800': {'number': '800',
                       'name': 'test_conf',
                       'pin_required': True,
                       'start_time': 12345.123,
                       'context': 'default',
                       'members': {1: {'join_order': 1,
                                       'join_time': 12345.123,
                                       'number': '1002',
                                       'name': 'Tester 1',
                                       'channel': 'sip/bcde-0987',
                                       'muted': True}}},
               '801': {'number': '801',
                       'name': 'conf2',
                       'pin_required': True,
                       'start_time': 12345.666,
                       'context': 'default',
                       'members': {1: {'join_order': 1,
                                       'join_time': 654534.324,
                                       'number': '1002',
                                       'name': 'Tester 1',
                                       'channel': 'sip/bcde-4567',
                                       'muted': True},
                                   2: {'join_order': 2,
                                       'join_time': 12345.123,
                                       'number': '1001',
                                       'name': 'Another tester',
                                       'channel': 'sip/abcd-1234',
                                       'muted': True}}}}

        self.notifier._current_state = msg
        self.notifier._send_meetme_membership()
        self.notifier._send_meetme_membership()  # Makes sure we don't send the same info twice

        client_1_membership = {'class': 'meetme_user',
                               'list': sorted([{'room_number': '801',
                                                'user_number': 2}])}
        client_2_membership = {'class': 'meetme_user',
                               'list': sorted([{'room_number': '800',
                                                'user_number': 1},
                                               {'room_number': '801',
                                                'user_number': 1}])}

        client_connection_1.send_message.assert_called_once_with(client_1_membership)
        client_connection_2.send_message.assert_called_once_with(client_2_membership)

    def test_get_room_number_for_chan_start(self):
        msg = {'800': {'number': '800',
                       'name': 'test_conf',
                       'pin_required': True,
                       'start_time': 12345.123,
                       'context': 'default',
                       'members': {1: {'join_order': 1,
                                       'join_time': 12345.123,
                                       'number': '1002',
                                       'name': 'Tester 1',
                                       'channel': 'sip/bcde-0987',
                                       'muted': True}}},
               '801': {'number': '801',
                       'name': 'conf2',
                       'pin_required': True,
                       'start_time': 12345.666,
                       'context': 'default',
                       'members': {1: {'join_order': 1,
                                       'join_time': 654534.324,
                                       'number': '1002',
                                       'name': 'Tester 1',
                                       'channel': 'sip/bcde-4567',
                                       'muted': True},
                                   2: {'join_order': 2,
                                       'join_time': 12345.123,
                                       'number': '1001',
                                       'name': 'Another tester',
                                       'channel': 'sip/abcd-1234',
                                       'muted': True}}}}

        self.notifier._current_state = msg

        chan_start_1 = 'sip/abcd'
        chan_start_2 = 'sip/bcde'
        chan_start_3 = 'sip/xxx'

        result_1 = self.notifier._get_room_number_for_chan_start(chan_start_1)
        result_2 = self.notifier._get_room_number_for_chan_start(chan_start_2)
        result_3 = self.notifier._get_room_number_for_chan_start(chan_start_3)

        self.assertEqual(result_1, [('801', 2)])
        for pair in [('800', 1), ('801', 1)]:
            self.assertTrue(pair in result_2)
        self.assertEqual(result_3, [])
