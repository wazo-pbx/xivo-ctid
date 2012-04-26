from collections import namedtuple

import logging

logger = logging.getLogger(__name__)

QueueEntry = namedtuple('QueueEntry', ['position', 'name', 'number'])

NAME = 'CallerIDName'
NUMBER = 'CallerIDNum'
POSITION = 'Position'
QUEUE = 'Queue'
UNIQUE_ID = 'Uniqueid'

class QueueEntryManager(object):

    def __init__(self):
        self._queue_entries = {}

    def handle_join_event(self, event):
        try:
            entry = QueueEntry(event[POSITION], event[NAME], event[NUMBER])
            queue_name = event[QUEUE]
            unique_id = event[UNIQUE_ID]
            if queue_name not in self._queue_entries:
                self._queue_entries[queue_name] = {}
            self._queue_entries[queue_name][unique_id] = entry
            self._count_check()
        except Exception:
            logger.exception('Failed to update queue entries from %s', event)

    def handle_leave_event(self, event):
        try:
            queue_name = event[QUEUE]
            unique_id = event[UNIQUE_ID]
            if queue_name in self._queue_entries and unique_id in self._queue_entries[queue_name]:
                self._queue_entries[queue_name].pop(unique_id)
            self._count_check()
        except Exception:
            logger.exception('Did not remove queue entry')

    def _count_check(self, queue_name, expected_count):
        if queue_name in self._queue_entries:
            assert(expected_count == len(self._queue_entries[queue_name]))
        else:
            assert(expected_count == 0)
