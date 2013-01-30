# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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
import time

from mock import patch
from mock import Mock
from hamcrest import *

from xivo_cti.scheduler import Scheduler
from xivo_cti.dao import queue_dao
from xivo_cti.dao import channel_dao
from xivo_cti.dao import user_dao
from xivo_cti.services.current_call import formatter
from xivo_cti.services.current_call import manager
from xivo_cti.services.current_call import notifier
from xivo_cti.services.current_call.manager import PEER_CHANNEL
from xivo_cti.services.current_call.manager import LINE_CHANNEL
from xivo_cti.services.current_call.manager import BRIDGE_TIME
from xivo_cti.services.current_call.manager import ON_HOLD
from xivo_cti.services.current_call.manager import TRANSFER_CHANNEL
from xivo_cti import dao
from xivo_cti.services.device.manager import DeviceManager
from xivo_cti import xivo_ami


class TestCurrentCallManager(unittest.TestCase):

    def setUp(self):
        self.scheduler = Mock(Scheduler)
        self.device_manager = Mock(DeviceManager)
        self.notifier = Mock(notifier.CurrentCallNotifier)
        self.formatter = Mock(formatter.CurrentCallFormatter)
        self.ami_class = Mock(xivo_ami.AMIClass)

        self.manager = manager.CurrentCallManager(
            self.notifier,
            self.formatter,
            self.ami_class,
            self.scheduler,
            self.device_manager
        )

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

    def test_masquerade_agent_call(self):
        line_1 = u'sip/6s7foq'
        line_2 = u'sip/pcm_dev'
        local_line_1 = u'local/id-292@agentcallback;1'
        local_line_2 = u'local/id-292@agentcallback;2'

        line_1_channel = u'SIP/6s7foq-00000023'
        line_2_channel = u'SIP/pcm_dev-00000022'
        local_line_1_channel = u'Local/id-292@agentcallback-00000013;1'

        self.manager._calls_per_line = {
            local_line_1: [{BRIDGE_TIME: 1358197027.3219039,
                            PEER_CHANNEL: line_2_channel,
                            LINE_CHANNEL: local_line_1_channel,
                            ON_HOLD: False}],
            local_line_2: [{BRIDGE_TIME: 1358197027.242239,
                            PEER_CHANNEL: line_1_channel,
                            LINE_CHANNEL: u'Local/id-292@agentcallback-00000013;2',
                            ON_HOLD: False}],
            line_1: [{BRIDGE_TIME: 1358197027.2422481,
                      PEER_CHANNEL: u'Local/id-292@agentcallback-00000013;2',
                      LINE_CHANNEL: line_1_channel,
                      ON_HOLD: False}],
            line_2: [{BRIDGE_TIME: 1358197027.3218949,
                      PEER_CHANNEL: local_line_1_channel,
                      LINE_CHANNEL: line_2_channel,
                      ON_HOLD: False}]}

        self.manager.masquerade(local_line_1_channel, line_1_channel)

        expected = {
            line_1: [{BRIDGE_TIME: 1358197027.2422481,
                      PEER_CHANNEL: line_2_channel,
                      LINE_CHANNEL: line_1_channel,
                      ON_HOLD: False}],
            line_2: [{BRIDGE_TIME: 1358197027.3218949,
                      PEER_CHANNEL: line_1_channel,
                      LINE_CHANNEL: u'SIP/pcm_dev-00000022',
                      ON_HOLD: False}]
        }

        self.assertEqual(self.manager._calls_per_line, expected)

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

        self.manager.bridge_channels(self.channel_1, self.channel_2)

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

        self.manager.end_call(self.channel_1)

        expected = {
            self.line_1: [
                {PEER_CHANNEL: 'SIP/mytrunk-12345',
                 LINE_CHANNEL: 'SIP/tc8nb4-000002',
                 BRIDGE_TIME: bridge_time,
                 ON_HOLD: True}
            ],
        }

        self.assertEqual(self.manager._calls_per_line, expected)
        calls = self._get_notifier_calls()
        assert_that(calls, only_contains(self.line_1, self.line_2))

    def test_remove_transfer_channel(self):
        line = u'SIP/6s7foq'.lower()
        channel = u'%s-0000007b' % line
        transfer_channel = u'Local/1003@pcm-dev-00000021;1'

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
        transfer_channel = u'Local/1003@pcm-dev-00000021;1'

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

    def test_line_identity_from_channel(self):
        result = self.manager._identity_from_channel(self.channel_1)

        self.assertEqual(result, self.line_1)

    def test_line_identity_from_channel_local_channels(self):
        local_chan = u'Local/id-292@agentcallback-0000000f;1'
        expected = u'Local/id-292@agentcallback;1'.lower()

        result = self.manager._identity_from_channel(local_chan)

        self.assertEqual(result, expected)

    def _get_notifier_calls(self):
        return [call[0][0] for call in self.notifier.publish_current_call.call_args_list]

    @patch('xivo_dao.user_dao.get_line_identity')
    def test_hangup(self, mock_get_line_identity):
        user_id = 5
        self.manager._calls_per_line = {
            self.line_1: [
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: self.channel_1,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
            self.line_2: [
                {PEER_CHANNEL: self.channel_1,
                 LINE_CHANNEL: self.channel_2,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
        }
        mock_get_line_identity.return_value = self.line_1

        self.manager.hangup(user_id)

        self.manager.ami.sendcommand.assert_called_once_with('Hangup', [('Channel', self.channel_2)])

    @patch('xivo_dao.user_dao.get_line_identity')
    def test_complete_transfer(self, mock_get_line_identity):
        user_id = 5
        self.manager._calls_per_line = {
            self.line_1: [
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: self.channel_1,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
            self.line_2: [
                {PEER_CHANNEL: self.channel_1,
                 LINE_CHANNEL: self.channel_2,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
        }
        mock_get_line_identity.return_value = self.line_1

        self.manager.complete_transfer(user_id)

        self.manager.ami.sendcommand.assert_called_once_with(
            'Hangup',
            [('Channel', self.channel_1)]
        )

    @patch('xivo_dao.user_dao.get_line_identity')
    def test_complete_transfer_no_call(self, mock_get_line_identity):
        user_id = 5
        self.manager._calls_per_line = {
            self.line_1: [
            ],
        }
        mock_get_line_identity.return_value = self.line_1

        self.manager.complete_transfer(user_id)

    @patch('xivo_dao.user_dao.get_line_identity')
    def test_attended_transfer(self, mock_get_line_identity):
        user_id = 5
        number = '1234'
        line_context = 'ctx'
        self.manager._calls_per_line = {
            self.line_1: [
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: self.channel_1,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
            self.line_2: [
                {PEER_CHANNEL: self.channel_1,
                 LINE_CHANNEL: self.channel_2,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
        }
        mock_get_line_identity.return_value = self.line_1
        dao.user = Mock(user_dao.UserDAO)
        dao.user.get_context.return_value = line_context

        self.manager.attended_transfer(user_id, number)

        self.manager.ami.sendcommand.assert_called_once_with(
            'Atxfer', [
                ('Channel', self.channel_1),
                ('Exten', number),
                ('Context', line_context),
                ('Priority', '1')
            ]
        )

    @patch('xivo_dao.user_dao.get_line_identity')
    def test_hangup_no_line(self, mock_get_line_identity):
        user_id = 5
        mock_get_line_identity.side_effect = LookupError()

        self.manager.hangup(user_id)

        self.assertEqual(self.manager.ami.sendcommand.call_count, 0)

    @patch('xivo_dao.user_dao.get_line_identity')
    def test_switchboard_hold(self, mock_get_line_identity):
        dao.queue = Mock(queue_dao.QueueDAO)
        dao.queue.get_number_context_from_name.return_value = '3006', 'ctx'
        queue_name = 'queue_on_hold'
        user_id = 7
        mock_get_line_identity.return_value = self.line_2

        self.manager._calls_per_line = {
            self.line_1: [
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: self.channel_1,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
            self.line_2: [
                {PEER_CHANNEL: self.channel_1,
                 LINE_CHANNEL: self.channel_2,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
        }

        self.manager.switchboard_hold(user_id, queue_name)

        self.manager.ami.transfer.assert_called_once_with(self.channel_1, '3006', 'ctx')

    @patch('xivo_dao.user_dao.get_line_identity')
    def test_switchboard_unhold(self, mock_get_line_identity):
        unique_id = '1234567.44'
        user_id = 5
        user_line = 'sccp/12345'
        channel_to_intercept = 'SIP/acbdf-348734'
        transfer_option = ',Tx'
        bridge_options = channel_to_intercept + transfer_option
        cid_name, cid_number = 'Alice', '5565'
        delay = 0.25

        dao.channel = Mock(channel_dao.ChannelDAO)
        dao.channel.get_channel_from_unique_id.return_value = channel_to_intercept
        dao.channel.get_caller_id_name_number.return_value = cid_name, cid_number
        mock_get_line_identity.return_value = user_line
        self.manager.schedule_answer = Mock()

        self.manager.switchboard_unhold(user_id, unique_id)

        self.manager.ami.sendcommand.assert_called_once_with(
            'Originate',
            [('Channel', user_line),
             ('Application', 'Bridge'),
             ('Data', bridge_options),
             ('CallerID', '"%s" <%s>' % (cid_name, cid_number)),
             ('Async', 'true')]
        )

        self.manager.schedule_answer.assert_called_once_with(user_id, delay)

    @patch('xivo_dao.user_dao.get_line_identity')
    def test_switchboard_unhold_no_line(self, mock_get_line_identity):
        unique_id = '1234567.44'
        user_id = 5
        channel_to_intercept = 'SIP/acbdf-348734'

        dao.channel = Mock(channel_dao.ChannelDAO)
        dao.channel.get_channel_from_unique_id.return_value = channel_to_intercept
        mock_get_line_identity.side_effect = LookupError('No such line')

        self.assertRaises(LookupError, self.manager.switchboard_unhold, user_id, unique_id)

    @patch('xivo_dao.user_dao.get_line_identity')
    def test_switchboard_unhold_no_channel(self, mock_get_line_identity):
        unique_id = '1234567.44'
        user_id = 5
        user_line = 'sccp/12345'

        dao.channel = Mock(channel_dao.ChannelDAO)
        dao.channel.get_channel_from_unique_id.side_effect = LookupError()
        mock_get_line_identity.return_value = user_line

        self.assertRaises(LookupError, self.manager.switchboard_unhold, user_id, unique_id)

    @patch('xivo_dao.user_dao.get_device_id')
    def test_schedule_answer(self, mock_get_device_id):
        user_id = 6
        delay = 0.25
        device_id = 14
        mock_get_device_id.return_value = device_id

        self.manager.schedule_answer(user_id, delay)

        self.scheduler.schedule.assert_called_once_with(
            delay, self.device_manager.answer, device_id
        )

    def test_set_transfer_channel(self):
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
        call = filter(lambda c: c[LINE_CHANNEL] == channel, calls)[0]

        self.assertEqual(call[TRANSFER_CHANNEL], transfer_channel)

    def test_set_transfer_channel_not_tracked(self):
        line = u'SIP/6s7foq'.lower()
        channel = u'%s-0000007b' % line
        transfer_channel = u'Local/1003@pcm-dev-00000021;1'

        self.manager.set_transfer_channel(channel, transfer_channel)

    @patch('xivo_dao.user_dao.get_line_identity')
    def test_cancel_transfer(self, mock_get_line_identity):
        local_transfer_channel = u'Local/1003@pcm-dev-00000032;'
        transfer_channel = local_transfer_channel + u'1'
        transfered_channel = local_transfer_channel + u'2'
        user_id = 5
        self.manager._calls_per_line = {
            self.line_1: [
                {PEER_CHANNEL: self.channel_2,
                 LINE_CHANNEL: self.channel_1,
                 BRIDGE_TIME: 1234,
                 TRANSFER_CHANNEL: transfer_channel,
                 ON_HOLD: False}
            ],
            self.line_2: [
                {PEER_CHANNEL: self.channel_1,
                 LINE_CHANNEL: self.channel_2,
                 BRIDGE_TIME: 1234,
                 ON_HOLD: False}
            ],
        }
        mock_get_line_identity.return_value = self.line_1

        self.manager.cancel_transfer(user_id)

        self.manager.ami.sendcommand.assert_called_once_with(
            'Hangup',
            [('Channel', transfered_channel)]
        )

    def test_local_channel_peer(self):
        local_channel = u'Local/1003@pcm-dev-00000032;'
        mine = local_channel + u'1'
        peer = local_channel + u'2'

        result = self.manager._local_channel_peer(mine)

        self.assertEqual(result, peer)

        result = self.manager._local_channel_peer(peer)

        self.assertEqual(result, mine)
