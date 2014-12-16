# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

import time
import unittest
from mock import Mock
from mock import patch
from xivo_dao import queue_dao
from xivo_cti.dao.queue_dao import QueueDAO
from xivo_cti.services.queue_entry_manager import QueueEntryManager
from xivo_cti.services.queue_entry_manager import QueueEntry
from xivo_cti.services import queue_entry_manager
from xivo_cti.services.queue_entry_notifier import QueueEntryNotifier
from xivo_cti.services.queue_entry_encoder import QueueEntryEncoder
from xivo_cti.statistics.statistics_notifier import StatisticsNotifier
from xivo_cti.xivo_ami import AMIClass

QUEUE_NAME = 'testqueue'
QUEUE_ID = 77

CALLER_ID_NAME_1, CALLER_ID_NUMBER_1, UNIQUE_ID_1 = 'Super Tester', '111', '12345677.99'
CALLER_ID_NAME_2, CALLER_ID_NUMBER_2, UNIQUE_ID_2 = 'Second Tester', '222', '123543121.43'
CALLER_ID_NAME_3, CALLER_ID_NUMBER_3, UNIQUE_ID_3 = 'Third Guy', '333', '13498754.44'

TIME_NOW = time.time()
JOIN_TIME_1 = TIME_NOW
JOIN_TIME_2 = JOIN_TIME_1 + 5
JOIN_TIME_3 = JOIN_TIME_1 + 24

WAIT_TIME_1 = 13

JOIN_MESSAGE_2 = {'Event': 'Join',
                  'Privilege': 'call,all',
                  'Channel': 'SIP/my_trunk-1235',
                  'CallerIDNum': CALLER_ID_NUMBER_2,
                  'CallerIDName': CALLER_ID_NAME_2,
                  'ConnectedLineNum': 'unknown',
                  'ConnectedLineName': 'unknown',
                  'Queue': QUEUE_NAME,
                  'Position': '2',
                  'Count': '2',
                  'Uniqueid': UNIQUE_ID_2}

QUEUE_ENTRY_1 = QueueEntry(1, CALLER_ID_NAME_1, CALLER_ID_NUMBER_1, JOIN_TIME_1, UNIQUE_ID_1)
QUEUE_ENTRY_2 = QueueEntry(2, CALLER_ID_NAME_2, CALLER_ID_NUMBER_2, JOIN_TIME_2, UNIQUE_ID_2)

LEAVE_MESSAGE_1 = {'Event': 'Leave',
                   'Privilege': 'call,all',
                   'Channel': 'SIP/pcm_dev-0000001f',
                   'Queue': QUEUE_NAME,
                   'Count': '0',
                   'Position': '1',
                   'Uniqueid': UNIQUE_ID_1}


JOIN_MESSAGE_1 = {'Event': 'Join',
                  'Privilege': 'call,all',
                  'Channel': 'SIP/my_trunk-1234',
                  'CallerIDNum': CALLER_ID_NUMBER_1,
                  'CallerIDName': CALLER_ID_NAME_1,
                  'ConnectedLineNum': 'unknown',
                  'ConnectedLineName': 'unknown',
                  'Queue': QUEUE_NAME,
                  'Position': '1',
                  'Count': '1',
                  'Uniqueid': UNIQUE_ID_1}

QUEUE_ENTRY_MESSAGE = {'Event': 'QueueEntry',
                       'Queue': QUEUE_NAME,
                       'Position': '1',
                       'Channel': 'SIP/pcm_dev-00000029',
                       'Uniqueid': UNIQUE_ID_1,
                       'CallerIDNum': CALLER_ID_NUMBER_1,
                       'CallerIDName': CALLER_ID_NAME_1,
                       'ConnectedLineNum': 'unknown',
                       'ConnectedLineName': 'unknown',
                       'Wait': str(WAIT_TIME_1)}


class TestQueueEntryManager(unittest.TestCase):

    def setUp(self):
        self.encoder = Mock(QueueEntryEncoder)
        self.notifier = Mock(QueueEntryNotifier)
        self.statistics_notifier = Mock(StatisticsNotifier)
        ami_class = Mock(AMIClass)
        self.manager = QueueEntryManager(self.notifier,
                                         self.encoder,
                                         self.statistics_notifier,
                                         ami_class)

    def tearDown(self):
        QueueEntryManager._instance = None

    @patch('time.time', Mock(return_value=JOIN_TIME_1))
    @patch('xivo_dao.queue_dao.id_from_name', Mock())
    @patch('xivo_cti.dao.queue', spec=QueueDAO)
    def _join_1(self, mock_queue_dao):
        mock_queue_dao.exists.return_value = True
        self.manager.join(QUEUE_NAME, 1, 1, CALLER_ID_NAME_1, CALLER_ID_NUMBER_1, UNIQUE_ID_1)

    @patch('time.time', Mock(return_value=JOIN_TIME_2))
    @patch('xivo_dao.queue_dao.id_from_name', Mock())
    @patch('xivo_cti.dao.queue', spec=QueueDAO)
    def _join_2(self, mock_queue_dao):
        mock_queue_dao.exists.return_value = True
        self.manager.join(QUEUE_NAME, 2, 2, CALLER_ID_NAME_2, CALLER_ID_NUMBER_2, UNIQUE_ID_2)

    @patch('time.time', Mock(return_value=JOIN_TIME_3))
    @patch('xivo_dao.queue_dao.id_from_name', Mock())
    @patch('xivo_cti.dao.queue', spec=QueueDAO)
    def _join_3(self, mock_queue_dao):
        mock_queue_dao.exists.return_value = True
        self.manager.join(QUEUE_NAME, 3, 3, CALLER_ID_NAME_3, CALLER_ID_NUMBER_3, UNIQUE_ID_3)

    @patch('xivo_cti.ioc.context.context.get')
    def test_parse_new_entry(self, mock_context):
        self.manager.join = Mock()
        mock_context.return_value = self.manager

        queue_entry_manager.parse_join(JOIN_MESSAGE_1)

        self.manager.join.assert_called_once_with(QUEUE_NAME, 1, 1, CALLER_ID_NAME_1, CALLER_ID_NUMBER_1, UNIQUE_ID_1)

    @patch('xivo_cti.ioc.context.context.get')
    def test_parse_queue_status_complete(self, mock_context):
        msg = {'Event': 'QueueStatusComplete'}
        self.manager.publish = Mock()
        mock_context.return_value = self.manager

        queue_entry_manager.parse_queue_status_complete(msg)

        self.manager.publish.assert_called_once_with()

    @patch('xivo_cti.ioc.context.context.get')
    def test_parse_queue_entry(self, mock_context):
        self.manager.insert = Mock()
        mock_context.return_value = self.manager

        queue_entry_manager.parse_queue_entry(QUEUE_ENTRY_MESSAGE)

        self.manager.insert.assert_called_once_with(
            QUEUE_NAME,
            1,
            CALLER_ID_NAME_1,
            CALLER_ID_NUMBER_1,
            UNIQUE_ID_1,
            WAIT_TIME_1
        )

    def test_new_entry(self):
        self._join_1()

        self.assertTrue(QUEUE_NAME in self.manager._queue_entries)

        entry = self.manager._queue_entries[QUEUE_NAME][UNIQUE_ID_1]

        self.assertEqual(entry, QUEUE_ENTRY_1)

    def test_multiple_entries(self):
        self._join_1()
        self._join_2()

        count = len(self.manager._queue_entries[QUEUE_NAME])

        self.assertEqual(count, 2)

        self.assertEquals(QUEUE_ENTRY_1, self.manager._queue_entries[QUEUE_NAME][UNIQUE_ID_1])
        self.assertEquals(QUEUE_ENTRY_2, self.manager._queue_entries[QUEUE_NAME][UNIQUE_ID_2])

    @patch('xivo_cti.ioc.context.context.get')
    def test_handle_leave(self, mock_context):
        self.manager.leave = Mock()
        mock_context.return_value = self.manager

        queue_entry_manager.parse_leave(LEAVE_MESSAGE_1)

        self.manager.leave.assert_called_once_with(QUEUE_NAME, 1, 0, UNIQUE_ID_1)

    @patch('xivo_dao.queue_dao.id_from_name', Mock())
    @patch('xivo_cti.dao.queue', spec=QueueDAO)
    def test_leave_event(self, mock_queue_dao):
        mock_queue_dao.exists.return_value = True
        self._join_1()
        self._join_2()

        self.manager.leave(QUEUE_NAME, 1, 1, UNIQUE_ID_1)

        count = len(self.manager._queue_entries[QUEUE_NAME])

        self.assertEqual(count, 1)

    @patch('xivo_dao.queue_dao.id_from_name', Mock())
    @patch('xivo_cti.dao.queue', spec=QueueDAO)
    def test_count_check(self, mock_queue_dao):
        mock_queue_dao.exists.return_value = True
        self._join_1()

        self.assertRaises(AssertionError,
                          lambda: self.manager._count_check(QUEUE_NAME, 0))

        self.manager._count_check(QUEUE_NAME, 1)

        self.assertRaises(AssertionError,
                          lambda: self.manager._count_check(QUEUE_NAME, 2))

    def test_count_check_no_queue(self):
        self.assertRaises(AssertionError,
                          lambda: self.manager._count_check('not_a_queue', 3))

    def test_count_check_untracked_queue(self):
        self.manager._count_check('un-tracked', 0)
        self.assertRaises(AssertionError,
                          lambda: self.manager._count_check('un-tracked', 1))

    @patch('xivo_dao.queue_dao.id_from_name', Mock())
    @patch('xivo_cti.dao.queue', spec=QueueDAO)
    def test_position_change(self, mock_queue_dao):
        mock_queue_dao.exists.return_value = True
        self._join_1()
        self._join_2()
        self._join_3()

        entries = self.manager._queue_entries[QUEUE_NAME]

        self.assertEqual(entries[UNIQUE_ID_1].position, 1)
        self.assertEqual(entries[UNIQUE_ID_2].position, 2)
        self.assertEqual(entries[UNIQUE_ID_3].position, 3)

        # 2 leaves the queue, new order => 1, 3

        self.manager.leave(QUEUE_NAME, 2, 2, UNIQUE_ID_2)

        self.assertEqual(entries[UNIQUE_ID_1].position, 1)
        self.assertEqual(entries[UNIQUE_ID_3].position, 2)

    def test_decrement_position(self):
        self.manager._queue_entries[QUEUE_NAME] = {}
        entries = self.manager._queue_entries[QUEUE_NAME]
        entries[1] = QueueEntry(1, 'one', '111', time.time(), '111.11')
        entries[2] = QueueEntry(2, 'two', '222', time.time(), '222.22')
        entries[3] = QueueEntry(3, 'three', '333', time.time(), '333.33')
        entries[4] = QueueEntry(4, 'four', '444', time.time(), '444.44')

        # 1 leaves the queue (pos 1)
        entries.pop(1)

        self.manager._decrement_position(QUEUE_NAME, 1)

        self.assertEqual(entries[2].position, 1)
        self.assertEqual(entries[3].position, 2)
        self.assertEqual(entries[4].position, 3)

        # 3 leaves the queue (pos 2)
        entries.pop(3)

        self.manager._decrement_position(QUEUE_NAME, 2)

        self.assertEqual(entries[2].position, 1)
        self.assertEqual(entries[4].position, 2)

    @patch('time.time', Mock(return_value=JOIN_TIME_1))
    def test_update(self):
        expected = QueueEntry(1, CALLER_ID_NAME_1, CALLER_ID_NUMBER_1, JOIN_TIME_1 - WAIT_TIME_1, UNIQUE_ID_1)

        self.manager.insert(QUEUE_NAME, 1, CALLER_ID_NAME_1, CALLER_ID_NUMBER_1,
                            UNIQUE_ID_1, WAIT_TIME_1)

        entry = self.manager._queue_entries[QUEUE_NAME][UNIQUE_ID_1]

        self.assertEquals(entry, expected)

    def test_clear_data(self):
        self._join_1()
        self._join_2()

        self.manager.clear_data(QUEUE_NAME)

        self.assertFalse(QUEUE_NAME in self.manager._queue_entries)

    @patch('xivo_cti.ioc.context.context.get')
    def test_parse_queue_params(self, mock_context):
        msg = {'Event': 'QueueParams',
               'Queue': QUEUE_NAME,
               'Max': '0',
               'Strategy': 'ringall',
               'Calls': '1',
               'Holdtime': '12',
               'TalkTime': '0',
               'Completed': '14',
               'Abandoned': '5',
               'ServiceLevel': '0',
               'ServicelevelPerf': '0.0',
               'Weight': '0'}

        self.manager.clear_data = Mock()
        mock_context.return_value = self.manager

        queue_entry_manager.parse_queue_params(msg)

        self.manager.clear_data.assert_called_once_with(QUEUE_NAME)

    def test_synchronize_queue_all(self):
        ami_class = Mock(AMIClass)
        self.manager._ami = ami_class

        self.manager.synchronize()

        self.assertTrue(ami_class.sendqueuestatus.called)

        self.manager._ami = None

    def test_synchronize_queue(self):
        ami_class = Mock()

        self.manager._ami = ami_class

        self.manager.synchronize(QUEUE_NAME)

        ami_class.sendqueuestatus.assert_called_once_with(QUEUE_NAME)

    @patch('xivo_dao.queue_dao.id_from_name', Mock())
    @patch('xivo_dao.queue_dao.queue_name', Mock())
    @patch('xivo_cti.dao.queue', spec=QueueDAO)
    def test_publish(self, mock_queue_dao):
        mock_queue_dao.exists.return_value = True
        msg = {'encoded': 'result'}
        self.manager._encoder = Mock(QueueEntryEncoder)
        queue_dao.queue_name.return_value = QUEUE_NAME
        self.manager._encoder.encode.return_value = msg
        self._subscriber_called = False

        self._join_1()
        self._join_2()
        self._join_3()
        self.notifier.publish.reset_mock()

        self.manager.publish(QUEUE_NAME)

        self.notifier.publish.assert_called_once_with(QUEUE_NAME, msg)

    @patch('time.time', Mock(return_value=98797987))
    @patch('xivo_dao.queue_dao.id_from_name', return_value=QUEUE_ID)
    @patch('xivo_cti.dao.queue', spec=QueueDAO)
    def test_publish_longest_wait_time_no_call_in_queue(self, mock_queue_dao, mock_id_from_name):
        mock_queue_dao.exists.return_value = True
        self.manager.join(QUEUE_NAME, 1, 1, CALLER_ID_NAME_1, CALLER_ID_NUMBER_1, UNIQUE_ID_1)

        mock_id_from_name.assert_called_with(QUEUE_NAME)
        self.manager._statistics_notifier.on_stat_changed.assert_called_with(
            {
                '%s' % QUEUE_ID: {
                    'Xivo-WaitingCalls': 1,
                    'Xivo-LongestWaitTime': 0
                }
            })

    @patch('xivo_cti.services.queue_entry_manager.longest_wait_time_calculator', return_value=789)
    @patch('xivo_dao.queue_dao.id_from_name', Mock(return_value=QUEUE_ID))
    @patch('xivo_cti.dao.queue', spec=QueueDAO)
    def test_publish_real_time_stats_on_leave_with_calls_in_queue(self, mock_queue_dao, mock_longest_wait_time_calculator):
        mock_queue_dao.exists.return_value = True
        self._join_1()
        self._join_2()

        self.manager._statistics_notifier.reset_mock()

        self.manager.leave(QUEUE_NAME, 1, 1, UNIQUE_ID_1)

        queue_dao.id_from_name.assert_called_with(QUEUE_NAME)
        mock_longest_wait_time_calculator.assert_called_with(self.manager._queue_entries[QUEUE_NAME])

        self.manager._statistics_notifier.on_stat_changed.assert_called_with(
            {
                '%s' % QUEUE_ID: {
                    'Xivo-WaitingCalls': 1,
                    'Xivo-LongestWaitTime': 789L
                }
            })

    @patch('xivo_dao.queue_dao.id_from_name', Mock(return_value=QUEUE_ID))
    @patch('xivo_cti.dao.queue', spec=QueueDAO)
    def test_publish_real_time_stats_on_leave_with_one_call_in_queue(self, mock_queue_dao):
        mock_queue_dao.exists.return_value = True
        self._join_1()

        self.manager._statistics_notifier.reset_mock()

        self.manager.leave(QUEUE_NAME, 1, 0, UNIQUE_ID_1)

        self.manager._statistics_notifier.on_stat_changed.assert_called_with(
            {
                '%s' % QUEUE_ID: {
                    'Xivo-WaitingCalls': 0
                }
            })

    @patch('time.time')
    @patch('xivo_dao.queue_dao.id_from_name', Mock(return_value=QUEUE_ID))
    @patch('xivo_cti.dao.queue', spec=QueueDAO)
    def test_calculate_longest_wait_time_one_call(self, mock_queue_dao, mock_time):
        mock_queue_dao.exists.return_value = True
        mock_time.return_value = long(TIME_NOW) - 300

        self.manager.join(QUEUE_NAME, 1, 1, CALLER_ID_NAME_1, CALLER_ID_NUMBER_1, UNIQUE_ID_1)

        mock_time.return_value = long(TIME_NOW)
        longest_wait_time = queue_entry_manager.longest_wait_time_calculator(self.manager._queue_entries[QUEUE_NAME])

        self.assertEquals(longest_wait_time, 300)

    @patch('time.time')
    @patch('xivo_dao.queue_dao.id_from_name', Mock(return_value=QUEUE_ID))
    @patch('xivo_cti.dao.queue', spec=QueueDAO)
    def test_calculate_longest_wait_time_multiple_calls(self, mock_queue_dao, mock_time):
        mock_queue_dao.exists.return_value = True
        mock_time.return_value = long(TIME_NOW) - 150
        self.manager.join(QUEUE_NAME, 1, 1, CALLER_ID_NAME_1, CALLER_ID_NUMBER_1, UNIQUE_ID_1)

        mock_time.return_value = long(TIME_NOW) - 400
        self.manager.join(QUEUE_NAME, 2, 2, CALLER_ID_NAME_2, CALLER_ID_NUMBER_2, UNIQUE_ID_2)

        mock_time.return_value = long(TIME_NOW)
        longest_wait_time = queue_entry_manager.longest_wait_time_calculator(self.manager._queue_entries[QUEUE_NAME])

        self.assertEquals(longest_wait_time, 400)

    @patch('xivo_cti.services.queue_entry_manager.longest_wait_time_calculator', Mock(return_value=765))
    @patch('xivo_dao.queue_dao.id_from_name', Mock())
    @patch('xivo_cti.dao.queue', spec=QueueDAO)
    def test_publish_all_realtime_stats(self, mock_queue_dao):
        mock_queue_dao.exists.return_value = True
        cti_connection = {}
        queue_ids = {'service': 56, 'boats': 34}

        self.manager.join('service', 1, 1, CALLER_ID_NAME_1, CALLER_ID_NUMBER_1, UNIQUE_ID_1)
        self.manager.join('boats', 1, 1, CALLER_ID_NAME_2, CALLER_ID_NUMBER_2, UNIQUE_ID_2)

        queue_dao.id_from_name.side_effect = lambda queue_name: queue_ids[queue_name]

        self.manager.publish_all_realtime_stats(cti_connection)

        self.manager._statistics_notifier.send_statistic.assert_was_called_with(
            {
                '%s' % 56: {
                    'Xivo-WaitingCalls': 1,
                    'Xivo-LongestWaitTime': 765
                }
            },
            cti_connection)
        self.manager._statistics_notifier.send_statistic.assert_was_called_with(
            {
                '%s' % 34: {
                    'Xivo-WaitingCalls': 1,
                    'Xivo-LongestWaitTime': 765
                }
            },
            cti_connection)

    @patch('xivo_cti.services.queue_entry_manager.longest_wait_time_calculator', Mock(return_value=765))
    @patch('xivo_dao.queue_dao.id_from_name', Mock(side_effect=LookupError('No such queue')))
    @patch('xivo_cti.dao.queue', spec=QueueDAO)
    def test_publish_all_realtime_stats_removed_queue(self, mock_queue_dao):
        mock_queue_dao.exists.return_value = False
        cti_connection = {}

        self.manager.join('service', 1, 1, CALLER_ID_NAME_1, CALLER_ID_NUMBER_1, UNIQUE_ID_1)

        queue_dao.id_from_name.side_effect = LookupError('No such queue')

        self.manager.publish_all_realtime_stats(cti_connection)

        self.assertFalse(self.manager._statistics_notifier.send_statistic.called)
        self.assertTrue('service' not in self.manager._queue_entries)

    @patch('xivo_cti.dao.queue', spec=QueueDAO)
    def test_join_group(self, mock_queue_dao):
        mock_queue_dao.exists.return_value = False
        self.manager.insert = Mock()

        self.manager.join('not_a_queue', 1, 1, CALLER_ID_NAME_1, CALLER_ID_NUMBER_1, UNIQUE_ID_1)

        self.assertFalse(self.manager.insert.called)

    @patch('xivo_cti.dao.queue', spec=QueueDAO)
    def test_leave_group(self, mock_queue_dao):
        mock_queue_dao.exists.return_value = False
        self.manager.synchronize = Mock()

        self.manager.leave('not_a_queue', 1, 1, UNIQUE_ID_1)

        self.assertFalse(self.manager.synchronize.called)
