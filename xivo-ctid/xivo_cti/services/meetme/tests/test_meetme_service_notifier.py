#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2012 Avencall
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
from mock import Mock, call
from xivo_cti.services.meetme.service_notifier import MeetmeServiceNotifier
from xivo_cti.services.meetme import encoder
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.client_connection import ClientConnection
from xivo_cti.dao.userfeaturesdao import UserFeaturesDAO
import Queue
from xivo_cti.cti_config import Config


class TestMeetmeServiceNotifier(unittest.TestCase):

    def setUp(self):
        self.ipbx_id = 'xivo_test'
        self.notifier = MeetmeServiceNotifier()
        self.notifier.events_cti = Queue.Queue()
        self.notifier.ipbx_id = self.ipbx_id
        self.config = Mock(Config)
        self.config.part_context.return_value = False
        Config.instance = self.config
        self.user_dao = Mock(UserFeaturesDAO)
        self.notifier.user_features_dao = self.user_dao

    def tearDown(self):
        Config.instance = None

    def test_prepare_message(self):
        result = self.notifier._prepare_message()

        self.assertEqual(result['tipbxid'], 'xivo_test')

    def test_add(self):
        meetme_id = 64
        expected = {"class": "getlist",
                    "function": "addconfig",
                    "listname": "meetmes",
                    "tipbxid": self.ipbx_id,
                    'list': [meetme_id]}

        self.notifier.add(meetme_id)

        self.assertTrue(self.notifier.events_cti.qsize() > 0)
        event = self.notifier.events_cti.get()
        self.assertEqual(event, expected)

    def test_subscribe_update(self):
        user_id = 5
        user_contexts = ['test_ctx']
        channel_pattern = 'SIP/abcde'
        user_features_dao = Mock(UserFeaturesDAO)
        user_features_dao.get_reachable_contexts.return_value = user_contexts
        user_features_dao.get_line_identity.return_value = channel_pattern

        client_connection = Mock(CTI)
        client_connection.user_features_dao = user_features_dao
        client_connection.user_id.return_value = user_id

        self.notifier.user_features_dao = user_features_dao
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

        expected_subscription = {'client_connection': client_connection,
                                 'contexts': user_contexts,
                                 'channel_start': channel_pattern,
                                 'membership': []}

        self.assertEqual(self.notifier._subscriptions[client_connection], expected_subscription)
        client_connection.send_message.assert_called_once_with(expected_msg)

    def test_publish_meetme_update(self):
        client_connection_1 = Mock(CTI)
        client_connection_2 = Mock(CTI)

        self.notifier._subscriptions = {client_connection_1: {'client_connection': client_connection_1,
                                                              'contexts': ['default'],
                                                              'channel_start': 'sip/abcd',
                                                              'membership': []},
                                        client_connection_2: {'client_connection': client_connection_2,
                                                              'contexts': ['default'],
                                                              'channel_start': 'sip/bcde',
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

        self.notifier.publish_meetme_update(msg)

        client_connection_1.send_message.assert_called_once_with(expected_msg)
        client_connection_2.send_message.assert_called_once_with(expected_msg)

    def test_publish_no_change(self):
        client_connection_1 = Mock(CTI)
        client_connection_2 = Mock(CTI)

        self.notifier._subscriptions = {client_connection_1: {'client_connection': client_connection_1,
                                                              'contexts': ['default'],
                                                              'channel_start': 'sip/abcd',
                                                              'membership': []},
                                        client_connection_2: {'client_connection': client_connection_2,
                                                              'contexts': ['default'],
                                                              'channel_start': 'sip/bcde',
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

    def test_publish_meetme_update_context_separation(self):
        self.config.part_context.return_value = True

        client_connection_1 = Mock(CTI)
        client_connection_2 = Mock(CTI)

        self.notifier._subscriptions = {client_connection_1: {'client_connection': client_connection_1,
                                                              'contexts': ['test'],
                                                              'channel_start': 'sip/abcd',
                                                              'membership': []},
                                        client_connection_2: {'client_connection': client_connection_2,
                                                              'contexts': ['default'],
                                                              'channel_start': 'sip/bcde',
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

        _push_to_client = Mock()
        self.notifier._push_to_client = _push_to_client
        self.notifier.publish_meetme_update(msg)

        self.assertEqual(self.notifier._current_state, msg)
        self.assertTrue(call(client_connection_1) in _push_to_client.call_args_list)
        self.assertTrue(call(client_connection_2) in _push_to_client.call_args_list)

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

        user_dao = Mock(UserFeaturesDAO)
        self.notifier.user_features_dao = user_dao
        self.notifier._current_state = msg
        self.notifier._push_to_client(client_connection)

        client_connection.send_message.assert_called_once_with(expected)
