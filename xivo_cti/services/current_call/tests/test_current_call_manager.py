# -*- coding: utf-8 -*-
# Copyright 2007-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import time
import unittest

from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import only_contains
from mock import Mock
from mock import patch
from mock import sentinel as s

from xivo_cti import dao
from xivo_cti.dao import channel_dao

from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.services.call.manager import CallManager
from xivo_cti.services.call.storage import CallStorage
from xivo_cti.services.current_call import formatter
from xivo_cti.services.current_call import manager
from xivo_cti.services.current_call import notifier
from xivo_cti.services.current_call.manager import BRIDGE_TIME
from xivo_cti.services.current_call.manager import LINE_CHANNEL
from xivo_cti.services.current_call.manager import ON_HOLD
from xivo_cti.services.current_call.manager import PEER_CHANNEL
from xivo_cti.services.current_call.manager import TRANSFER_CHANNEL
from xivo_cti.services.device.manager import DeviceManager
from xivo_cti import xivo_ami


class _BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.device_manager = Mock(DeviceManager)
        self.notifier = Mock(notifier.CurrentCallNotifier)
        self.formatter = Mock(formatter.CurrentCallFormatter)
        self.ami_class = Mock(xivo_ami.AMIClass)
        self.call_manager = Mock(CallManager)
        self.call_storage = Mock(CallStorage)
        self.bus_listener = Mock()
        self.task_queue = Mock()
        self.call_pickup_tracker = manager.CallPickupTracker()

        self.manager = manager.CurrentCallManager(
            self.notifier,
            self.formatter,
            self.ami_class,
            self.device_manager,
            self.call_manager,
            self.call_storage,
            self.bus_listener,
            self.task_queue,
            self.call_pickup_tracker,
        )

        self.line_1 = 'sip/tc8nb4'
        self.line_2 = 'sip/6s7foq'
        self.channel_1 = 'SIP/tc8nb4-00000004'
        self.channel_2 = 'SIP/6s7foq-00000005'


class TestCurrentCallManager(_BaseTestCase):

    @patch('time.time')
    def test_bridge_channels(self, mock_time):
        bridge_time = time.time()
        mock_time.return_value = bridge_time

        self.manager._bridge_channels(self.channel_1, self.channel_2)

        expected = {
            self.line_1: [
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: self.channel_1,
                 BRIDGE_TIME: bridge_time,
                 ON_HOLD: False}
            ],
            self.line_2: [
                {PEER_CHANNEL: self.channel_1,
                 LINE_CHANNEL: self.channel_2,
                 BRIDGE_TIME: bridge_time,
                 ON_HOLD: False}
            ],
        }

        self.assertEqual(self.manager._calls_per_line, expected)
        calls = self._get_notifier_calls()
        assert_that(calls, only_contains(self.line_1, self.line_2))

    @patch('time.time')
    def test_bridge_channels_transfer_answered(self, mock_time):
        bridge_time = time.time()
        mock_time.return_value = bridge_time

        transferer_channel = self.channel_1
        transferee_channel = 'Local/123@default-00000009;2'

        calls_per_line = {
            self.line_1: [
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: self.channel_1,
                 BRIDGE_TIME: bridge_time,
                 ON_HOLD: False,
                 TRANSFER_CHANNEL: transferee_channel}
            ],
        }
        unanswered_transfers = {
            transferee_channel: transferer_channel,
        }
        self.manager._calls_per_line = calls_per_line
        self.manager._unanswered_transfers = unanswered_transfers

        self.manager._bridge_channels(transferer_channel, transferee_channel)

        self.notifier.attended_transfer_answered.assert_called_once_with(self.line_1)

    @patch('time.time')
    def test_bridge_channels_transfer_answered_reverse_order(self, mock_time):
        bridge_time = time.time()
        mock_time.return_value = bridge_time

        transferer_channel = self.channel_1
        transferee_channel = 'Local/123@default-00000009;2'

        calls_per_line = {
            self.line_1: [
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: self.channel_1,
                 BRIDGE_TIME: bridge_time,
                 ON_HOLD: False,
                 TRANSFER_CHANNEL: transferee_channel}
            ],
        }
        unanswered_transfers = {
            transferee_channel: transferer_channel,
        }
        self.manager._calls_per_line = calls_per_line
        self.manager._unanswered_transfers = unanswered_transfers

        self.manager._bridge_channels(transferee_channel, transferer_channel)

        self.notifier.attended_transfer_answered.assert_called_once_with(self.line_1)

    @patch('time.time')
    def test_bridge_channels_transfer_answered_when_line_has_multiple_calls(self, mock_time):
        bridge_time = time.time()
        mock_time.return_value = bridge_time

        transferer_channel = self.channel_1
        transferee_channel = 'Local/123@default-00000009;2'

        calls_per_line = {
            self.line_1: [
                {PEER_CHANNEL: 'SIP/sdkfjh-00000000012',
                 LINE_CHANNEL: self.channel_1,
                 BRIDGE_TIME: bridge_time},
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: self.channel_1,
                 BRIDGE_TIME: bridge_time,
                 TRANSFER_CHANNEL: transferee_channel}
            ],
        }
        unanswered_transfers = {
            transferee_channel: transferer_channel,
        }
        self.manager._calls_per_line = calls_per_line
        self.manager._unanswered_transfers = unanswered_transfers

        self.manager._bridge_channels(transferer_channel, transferee_channel)

        self.notifier.attended_transfer_answered.assert_called_once_with(self.line_1)

    @patch('time.time')
    def test_bridge_channels_transfer_answered_not_tracked(self, mock_time):
        bridge_time = time.time()
        mock_time.return_value = bridge_time

        transferer_channel = self.channel_1
        transferee_channel = 'Local/123@default-00000009;2'

        calls_per_line = {
            self.line_1: [
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: self.channel_1,
                 BRIDGE_TIME: bridge_time,
                 ON_HOLD: False}
            ],
        }
        self.manager._calls_per_line = calls_per_line

        self.manager._bridge_channels(transferer_channel, transferee_channel)

        call_count = self.notifier.attended_transfer_answered.call_count
        self.assertEqual(call_count, 0)

    def test_bridge_channels_on_hold(self):
        bridge_time = 123456.44

        self.manager._calls_per_line = {
            self.line_1: [
                {PEER_CHANNEL: self.channel_2,
                 BRIDGE_TIME: bridge_time,
                 ON_HOLD: True}
            ],
            self.line_2: [
                {PEER_CHANNEL: self.channel_1,
                 BRIDGE_TIME: bridge_time,
                 ON_HOLD: False}
            ],
        }

        self.manager._bridge_channels(self.channel_1, self.channel_2)

        expected = {
            self.line_1: [
                {PEER_CHANNEL: self.channel_2,
                 BRIDGE_TIME: bridge_time,
                 ON_HOLD: True}
            ],
            self.line_2: [
                {PEER_CHANNEL: self.channel_1,
                 BRIDGE_TIME: bridge_time,
                 ON_HOLD: False}
            ],
        }

        self.assertEqual(self.manager._calls_per_line, expected)
        self.assertEqual(self.notifier.publish_current_call.call_count, 0)

    def test_on_local_optimization_missing_source_call(self):
        local_one_line = 'local/foo@bar;1'
        local_one_channel = 'Local/foo@bar-000001;1'
        local_two_line = 'local/foo@bar;2'
        local_two_channel = 'Local/foo@bar-000001;2'

        self.manager._calls_per_line = {
            local_one_line: [
                {PEER_CHANNEL: self.channel_1,
                 LINE_CHANNEL: local_one_channel},
            ],
            local_two_line: [
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: local_two_channel}
            ],
            self.line_2: [
                {PEER_CHANNEL: local_two_channel,
                 LINE_CHANNEL: self.channel_2},
            ]
        }

        self.manager.on_local_optimization(local_one_channel, local_two_channel)

        expected = {
            self.line_2: [
                {PEER_CHANNEL: self.channel_1,
                 LINE_CHANNEL: self.channel_2}
            ],
        }

        self.assertEqual(self.manager._calls_per_line, expected)

    def test_end_call(self):
        bridge_time = 123456.44

        self.manager._calls_per_line = {
            self.line_1: [
                {PEER_CHANNEL: 'SIP/mytrunk-12345',
                 LINE_CHANNEL: 'SIP/tc8nb4-000002',
                 BRIDGE_TIME: bridge_time,
                 ON_HOLD: True},
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: self.channel_1,
                 BRIDGE_TIME: bridge_time,
                 ON_HOLD: False},
            ],
            self.line_2: [
                {PEER_CHANNEL: self.channel_1,
                 LINE_CHANNEL: self.channel_2,
                 BRIDGE_TIME: bridge_time,
                 ON_HOLD: False}
            ],
        }
        self.manager._unanswered_transfers = {
            self.channel_1: 'SIP/foo-000122',
            self.channel_2: 'SIP/bar-000123',
        }

        self.manager.end_call(self.channel_1)

        expected = {
            self.line_1: [
                {PEER_CHANNEL: 'SIP/mytrunk-12345',
                 LINE_CHANNEL: 'SIP/tc8nb4-000002',
                 BRIDGE_TIME: bridge_time,
                 ON_HOLD: True}
            ],
        }
        expected_unanswered_transfers = {
            self.channel_2: 'SIP/bar-000123',
        }

        self.assertEqual(self.manager._calls_per_line, expected)
        self.assertEqual(self.manager._unanswered_transfers, expected_unanswered_transfers)
        calls = self._get_notifier_calls()
        assert_that(calls, only_contains(self.line_1, self.line_2))

    def test_remove_transfer_channel(self):
        line = u'SIP/6s7foq'.lower()
        channel = u'%s-0000007b' % line
        transfer_channel = u'Local/1003@pcm-dev-00000021;2'

        self.manager._calls_per_line = {
            line: [
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: channel,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False,
                 TRANSFER_CHANNEL: transfer_channel}
            ],
        }
        expected_calls_per_line = {
            line: [
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: channel,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
        }

        self.manager.remove_transfer_channel(transfer_channel)
        calls_per_line = self.manager._calls_per_line

        self.assertEqual(expected_calls_per_line, calls_per_line)
        self.notifier.publish_current_call.assert_called_once_with(line)

    def test_remove_transfer_channel_not_tracked(self):
        line = u'SIP/6s7foq'.lower()
        channel = u'%s-0000007b' % line
        transfer_channel = u'Local/1003@pcm-dev-00000021;2'

        self.manager._calls_per_line = {
            line: [
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: channel,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
        }

        self.manager.remove_transfer_channel(transfer_channel)

    def test_hold_channel(self):
        self.manager._calls_per_line = {
            self.line_1: [
                {PEER_CHANNEL: self.channel_2,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
            self.line_2: [
                {PEER_CHANNEL: self.channel_1,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
        }

        self.manager.hold_channel(self.channel_2)

        expected = {
            self.line_1: [
                {PEER_CHANNEL: self.channel_2,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: True}
            ],
            self.line_2: [
                {PEER_CHANNEL: self.channel_1,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
        }

        self.assertEqual(self.manager._calls_per_line, expected)
        self.notifier.publish_current_call.assert_called_once_with(self.line_1)

    def test_hold_channel_no_error_after_restart(self):
        self.manager.hold_channel(self.channel_2)

    def test_unhold_channel(self):
        self.manager._calls_per_line = {
            self.line_1: [
                {PEER_CHANNEL: self.channel_2,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: True}
            ],
            self.line_2: [
                {PEER_CHANNEL: self.channel_1,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
        }

        self.manager.unhold_channel(self.channel_2)

        expected = {
            self.line_1: [
                {PEER_CHANNEL: self.channel_2,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
            self.line_2: [
                {PEER_CHANNEL: self.channel_1,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
        }

        self.assertEqual(self.manager._calls_per_line, expected)
        self.notifier.publish_current_call.assert_called_once_with(self.line_1)

    def test_unhold_channel_no_error_after_restart(self):
        self.manager.unhold_channel(self.channel_2)

    def test_get_line_calls(self):
        self.manager._calls_per_line = {
            self.line_1: [
                {PEER_CHANNEL: self.channel_2,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: True}
            ],
            self.line_2: [
                {PEER_CHANNEL: self.channel_1,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
        }

        calls = self.manager.get_line_calls(self.line_1)

        self.assertEquals(calls, self.manager._calls_per_line[self.line_1])

    def test_get_line_calls_no_line(self):
        channel_1 = 'SIP/tc8nb4-00000004'
        channel_2 = 'SIP/6s7foq-00000005'
        self.manager._calls_per_line = {
            self.line_1: [
                {PEER_CHANNEL: channel_2,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: True}
            ],
            self.line_2: [
                {PEER_CHANNEL: channel_1,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
        }

        calls = self.manager.get_line_calls('SCCP/654')

        self.assertEquals(calls, [])

    @patch('xivo_cti.dao.queue')
    def test_that_switchboard_hold_calls_transfer_blind(self, mock_queue_dao):
        mock_queue_dao.get_number_context_from_name.return_value = s.queue_number, s.queue_context

        with patch.object(self.manager, '_call_manager') as call_manager:
            self.manager.switchboard_hold(s.connection, s.token, s.user_id, s.user_uuid, s.queue_name)

        mock_queue_dao.get_number_context_from_name.assert_called_once_with(s.queue_name)
        call_manager.transfer_blind.assert_called_once_with(s.connection, s.token, s.user_id, s.user_uuid, s.queue_number)

    @patch('xivo_dao.user_line_dao.get_line_identity_by_user_id', Mock())
    @patch('xivo_cti.services.current_call.manager.dao')
    def test_switchboard_retrieve_waiting_call_when_not_talking_then_retrieve_the_call(self, mock_dao):
        unique_id = '1234567.44'
        user_id = 5
        line_identity = 'sccp/12345'
        line_cid_name = 'John'
        line_cid_number = '123'
        line_callerid = '"%s" <%s>' % (line_cid_name, line_cid_number)
        line = {
            'identity': line_identity,
            'callerid': line_callerid,
        }
        ringing_channel = 'sccp/12345-0000001'
        channel_to_intercept = 'SIP/acbdf-348734'
        cid_name, cid_number = 'Alice', '5565'
        conn = Mock(CTI)

        mock_dao.channel.get_channel_from_unique_id.return_value = channel_to_intercept
        mock_dao.channel.get_caller_id_name_number.return_value = cid_name, cid_number
        mock_dao.channel.channels_from_identity.return_value = [ringing_channel]
        mock_dao.user.get_line.return_value = line
        mock_dao.user.get_line_identity.return_value = line_identity

        self.manager.switchboard_retrieve_waiting_call(user_id, unique_id, conn)

        self.manager.ami.hangup_with_cause_answered_elsewhere.assert_called_once_with(ringing_channel)
        self.manager.ami.switchboard_retrieve.assert_called_once_with(
            line_identity, channel_to_intercept, cid_name, cid_number, line_cid_name, line_cid_number)
        self.call_manager.answer_next_ringing_call.assert_called_once_with(conn, line_identity)
        assert_that(self.call_pickup_tracker.is_marked(unique_id), equal_to(True))

    @patch('xivo_dao.user_line_dao.get_line_identity_by_user_id', Mock())
    @patch('xivo_cti.services.current_call.manager.dao')
    def test_switchboard_retrieve_waiting_call_twice(self, mock_dao):
        unique_id = '1234567.44'
        user_id = 5
        line_identity = 'sccp/12345'
        line_cid_name = 'John'
        line_cid_number = '123'
        line_callerid = '"%s" <%s>' % (line_cid_name, line_cid_number)
        line = {
            'identity': line_identity,
            'callerid': line_callerid,
        }
        ringing_channel = 'sccp/12345-0000001'
        channel_to_intercept = 'SIP/acbdf-348734'
        cid_name, cid_number = 'Alice', '5565'
        conn = Mock(CTI)

        mock_dao.channel.get_channel_from_unique_id.return_value = channel_to_intercept
        mock_dao.channel.get_caller_id_name_number.return_value = cid_name, cid_number
        mock_dao.channel.channels_from_identity.return_value = [ringing_channel]
        mock_dao.user.get_line.return_value = line
        mock_dao.user.get_line_identity.return_value = line_identity

        # Call 1
        self.manager.switchboard_retrieve_waiting_call(user_id, unique_id, conn)

        self.call_manager.answer_next_ringing_call.assert_called_once_with(conn, line_identity)
        assert_that(self.call_pickup_tracker.is_marked(unique_id), equal_to(True))

        # Reset
        self.call_manager.answer_next_ringing_call.reset_mock()

        # Call 2
        self.manager.switchboard_retrieve_waiting_call(42, unique_id, Mock())

        self.call_manager.answer_next_ringing_call.assert_not_called()
        assert_that(self.call_pickup_tracker.is_marked(unique_id), equal_to(True))

    @patch('xivo_dao.user_line_dao.get_line_identity_by_user_id')
    def test_switchboard_retrieve_waiting_call_when_talking_then_do_nothing(self, mock_get_line_identity):
        unique_id = '1234567.44'
        user_id = 5
        user_line = 'sccp/12345'
        talking_channel = 'sccp/12345-0000001'
        channel_to_intercept = 'SIP/acbdf-348734'
        cid_name, cid_number = 'Alice', '5565'
        client_connection = Mock(CTI)
        self.manager._calls_per_line = {
            user_line: [
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: talking_channel,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
        }

        dao.channel = Mock(channel_dao.ChannelDAO)
        dao.channel.get_channel_from_unique_id.return_value = channel_to_intercept
        dao.channel.get_caller_id_name_number.return_value = cid_name, cid_number
        dao.channel.channels_from_identity.return_value = [talking_channel]
        mock_get_line_identity.return_value = user_line

        self.manager.switchboard_retrieve_waiting_call(user_id, unique_id, client_connection)

        assert_that(self.ami_class.switchboard_retrieve.call_count, equal_to(0))
        assert_that(self.call_pickup_tracker.is_marked(unique_id), equal_to(False))

    @patch('xivo_dao.user_line_dao.get_line_identity_by_user_id')
    def test_switchboard_retrieve_waiting_call_when_no_channel_then_return(self, mock_get_line_identity):
        unique_id = '1234567.44'
        user_id = 5
        user_line = 'sccp/12345'

        dao.channel = Mock(channel_dao.ChannelDAO)
        dao.channel.get_channel_from_unique_id.side_effect = LookupError()
        mock_get_line_identity.return_value = user_line
        client_connection = Mock(CTI)

        self.manager.switchboard_retrieve_waiting_call(user_id, unique_id, client_connection)

        call_count_retrieve = self.manager.ami.switchboard_retrieve.call_count
        self.assertEqual(call_count_retrieve, 0)
        assert_that(self.call_pickup_tracker.is_marked(unique_id), equal_to(False))

    def test_set_transfer_channel(self):
        line = u'SIP/6s7foq'.lower()
        channel = u'%s-0000007b' % line
        transfer_channel = u'Local/1003@pcm-dev-00000021;2'

        self.manager._calls_per_line = {
            line: [
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: channel,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
        }

        self.manager.set_transfer_channel(channel, transfer_channel)

        calls = self.manager._calls_per_line[line]
        call = [c for c in calls if c[LINE_CHANNEL] == channel][0]

        self.assertEqual(call[TRANSFER_CHANNEL], transfer_channel)
        self.assertEqual(self.manager._unanswered_transfers, {transfer_channel: channel})

    def test_set_transfer_channel_ignore_local_1_channel(self):
        line = u'SIP/6s7foq'.lower()
        channel = u'%s-0000007b' % line
        transfer_channel = u'Local/1003@pcm-dev-00000021;1'

        self.manager._calls_per_line = {
            line: [
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: channel,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
        }

        self.manager.set_transfer_channel(channel, transfer_channel)

        calls = self.manager._calls_per_line[line]
        call = [c for c in calls if c[LINE_CHANNEL] == channel][0]

        self.assertNotIn(TRANSFER_CHANNEL, call)

    def test_set_transfer_channel_not_tracked(self):
        line = u'SIP/6s7foq'.lower()
        channel = u'%s-0000007b' % line
        transfer_channel = u'Local/1003@pcm-dev-00000021;2'

        self.manager.set_transfer_channel(channel, transfer_channel)

    def test_local_channel_peer(self):
        local_channel = u'Local/1003@pcm-dev-00000032;'
        mine = local_channel + u'1'
        peer = local_channel + u'2'

        result = self.manager._local_channel_peer(mine)

        self.assertEqual(result, peer)

        result = self.manager._local_channel_peer(peer)

        self.assertEqual(result, mine)

    def test_get_cid_name_and_number(self):
        line = {
            'callerid': '"John" <123>',
        }

        cid_name, cid_num = self.manager._get_cid_name_and_number_from_line(line)

        self.assertEqual(cid_name, 'John')
        self.assertEqual(cid_num, '123')

    def test_get_cid_name_and_number_on_error(self):
        line = {
            'callerid': 'foobar',
        }

        cid_name, cid_num = self.manager._get_cid_name_and_number_from_line(line)

        self.assertEqual(cid_name, '')
        self.assertEqual(cid_num, '')

    def _get_notifier_calls(self):
        return [call[0][0] for call in self.notifier.publish_current_call.call_args_list]
