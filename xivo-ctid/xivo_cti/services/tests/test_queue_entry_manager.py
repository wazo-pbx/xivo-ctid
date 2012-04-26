import unittest

from xivo_cti.services.queue_entry_manager import QueueEntryManager
from xivo_cti.services.queue_entry_manager import QueueEntry


class TestQueueEntryManager(unittest.TestCase):

    QUEUE_NAME = 'testqueue'
    CALLER_ID_NAME = 'Super Tester'
    CALLER_ID_NAME_2 = 'Second Tester'
    CALLER_ID_NUMBER = '666'
    CALLER_ID_NUMBER_2 = '555'
    UNIQUE_ID_1 = '12346756547.34'
    UNIQUE_ID_2 = '99999999922.43'

    JOIN_MESSAGE_1 = {'Event': 'Join',
                      'Privilege': 'call,all',
                      'Channel': 'SIP/my_trunk-1234',
                      'CallerIDNum': CALLER_ID_NUMBER,
                      'CallerIDName': CALLER_ID_NAME,
                      'ConnectedLineNum': 'unknown',
                      'ConnectedLineName': 'unknown',
                      'Queue': QUEUE_NAME,
                      'Position': '1',
                      'Count': '1',
                      'Uniqueid': UNIQUE_ID_1}

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

    QUEUE_ENTRY_1 = QueueEntry('1', CALLER_ID_NAME, CALLER_ID_NUMBER)
    QUEUE_ENTRY_2 = QueueEntry('2', CALLER_ID_NAME_2, CALLER_ID_NUMBER_2)

    LEAVE_MESSAGE_1 = {'Event': 'Leave',
                       'Privilege': 'call,all',
                       'Channel': 'SIP/pcm_dev-0000001f',
                       'Queue': QUEUE_NAME,
                       'Count': '0',
                       'Position': '1',
                       'Uniqueid': UNIQUE_ID_1}

    def setUp(self):
        self.manager = QueueEntryManager()

    def test_new_entry(self):
        self.manager.handle_join_event(self.JOIN_MESSAGE_1)

        self.assertTrue(self.QUEUE_NAME in self.manager._queue_entries)

        entry = self.manager._queue_entries[self.QUEUE_NAME][self.UNIQUE_ID_1]

        self.assertEqual(entry, self.QUEUE_ENTRY_1)

    def test_multiple_entries(self):
        self.manager.handle_join_event(self.JOIN_MESSAGE_1)
        self.manager.handle_join_event(self.JOIN_MESSAGE_2)

        count = len(self.manager._queue_entries[self.QUEUE_NAME])

        self.assertEqual(count, 2)

        self.assertEquals(self.QUEUE_ENTRY_1, self.manager._queue_entries[self.QUEUE_NAME][self.UNIQUE_ID_1])
        self.assertEquals(self.QUEUE_ENTRY_2, self.manager._queue_entries[self.QUEUE_NAME][self.UNIQUE_ID_2])

    def test_leave_event(self):
        self.manager.handle_join_event(self.JOIN_MESSAGE_1)
        self.manager.handle_join_event(self.JOIN_MESSAGE_2)

        self.manager.handle_leave_event(self.LEAVE_MESSAGE_1)

        count = len(self.manager._queue_entries[self.QUEUE_NAME])

        print self.manager._queue_entries
        self.assertEqual(count, 1)

    def test_count_check(self):
        self.manager.handle_join_event(self.JOIN_MESSAGE_1)

        self.assertRaises(AssertionError,
                          lambda: self.manager._count_check(self.QUEUE_NAME, 0))

        self.manager._count_check(self.QUEUE_NAME, 1)

        self.assertRaises(AssertionError,
                          lambda: self.manager._count_check(self.QUEUE_NAME, 2))

    def test_count_check_no_queue(self):
        self.assertRaises(AssertionError,
                          lambda: self.manager._count_check('not_a_queue', 3))

    def test_count_check_untracked_queue(self):
        self.manager._count_check('un-tracked', 0)
        self.assertRaises(AssertionError,
                          lambda: self.manager._count_check('un-tracked', 1))
