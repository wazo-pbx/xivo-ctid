import unittest
from mock import Mock
from mock import patch

import time

from xivo_cti.services.queue_entry_manager import QueueEntryManager
from xivo_cti.services.queue_entry_manager import QueueEntry
from xivo_cti.services import queue_entry_manager

QUEUE_NAME = 'testqueue'

CALLER_ID_NAME_1, CALLER_ID_NUMBER_1, UNIQUE_ID_1 = 'Super Tester', '111', '12345677.99'
CALLER_ID_NAME_2, CALLER_ID_NUMBER_2, UNIQUE_ID_2 = 'Second Tester', '222', '123543121.43'
CALLER_ID_NAME_3, CALLER_ID_NUMBER_3, UNIQUE_ID_3 = 'Third Guy', '333', '13498754.44'

JOIN_TIME_1 = time.time()
JOIN_TIME_2 = JOIN_TIME_1 + 5
JOIN_TIME_3 = JOIN_TIME_1 + 24

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

QUEUE_ENTRY_1 = QueueEntry(1, CALLER_ID_NAME_1, CALLER_ID_NUMBER_1, JOIN_TIME_1)
QUEUE_ENTRY_2 = QueueEntry(2, CALLER_ID_NAME_2, CALLER_ID_NUMBER_2, JOIN_TIME_2)

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

my_time = Mock()


class TestQueueEntryManager(unittest.TestCase):

    def setUp(self):
        self.manager = QueueEntryManager.get_instance()

    def tearDown(self):
        self.manager._queue_entries = {}

    @patch('time.time', my_time)
    def _join_1(self):
        my_time.return_value = JOIN_TIME_1
        self.manager.join(QUEUE_NAME, 1, 1, CALLER_ID_NAME_1, CALLER_ID_NUMBER_1, UNIQUE_ID_1)

    @patch('time.time', my_time)
    def _join_2(self):
        my_time.return_value = JOIN_TIME_2
        self.manager.join(QUEUE_NAME, 2, 2, CALLER_ID_NAME_2, CALLER_ID_NUMBER_2, UNIQUE_ID_2)

    @patch('time.time', my_time)
    def _join_3(self):
        my_time.return_value = JOIN_TIME_3
        self.manager.join(QUEUE_NAME, 3, 3, CALLER_ID_NAME_3, CALLER_ID_NUMBER_3, UNIQUE_ID_3)

    def test_parse_new_entry(self):
        join, handler = self.manager.join, Mock()
        self.manager.join = handler

        queue_entry_manager.parse_join(JOIN_MESSAGE_1)

        handler.assert_called_once_with(QUEUE_NAME, 1, 1, CALLER_ID_NAME_1, CALLER_ID_NUMBER_1, UNIQUE_ID_1)

        self.manager.join = join

    def test_new_entry(self):
        self._join_1()

        self.assertTrue(QUEUE_NAME in self.manager._queue_entries)

        entry = self.manager._queue_entries[QUEUE_NAME][UNIQUE_ID_1]

        self.assertEqual(entry, QUEUE_ENTRY_1)

    @patch('time.time', my_time)
    def test_multiple_entries(self):
        self._join_1()
        self._join_2()

        count = len(self.manager._queue_entries[QUEUE_NAME])

        self.assertEqual(count, 2)

        self.assertEquals(QUEUE_ENTRY_1, self.manager._queue_entries[QUEUE_NAME][UNIQUE_ID_1])
        self.assertEquals(QUEUE_ENTRY_2, self.manager._queue_entries[QUEUE_NAME][UNIQUE_ID_2])

    def test_handle_leave(self):
        leave, handler = self.manager.leave, Mock()
        self.manager.leave = handler

        queue_entry_manager.parse_leave(LEAVE_MESSAGE_1)

        handler.assert_called_once_with(QUEUE_NAME, 1, 0, UNIQUE_ID_1)

        self.manager.leave = leave

    def test_leave_event(self):
        self._join_1()
        self._join_2()

        self.manager.leave(QUEUE_NAME, 1, 1, UNIQUE_ID_1)

        count = len(self.manager._queue_entries[QUEUE_NAME])

        self.assertEqual(count, 1)

    def test_count_check(self):
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

    def test_position_change(self):
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
        entries[1] = QueueEntry(1, 'one', '111', time.time())
        entries[2] = QueueEntry(2, 'two', '222', time.time())
        entries[3] = QueueEntry(3, 'three', '333', time.time())
        entries[4] = QueueEntry(4, 'four', '444', time.time())

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
