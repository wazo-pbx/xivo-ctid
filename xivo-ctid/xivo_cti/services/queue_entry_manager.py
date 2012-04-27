from collections import namedtuple

import logging

logger = logging.getLogger(__name__)

QueueEntry = namedtuple('QueueEntry', ['position', 'name', 'number'])

NAME = 'CallerIDName'
NUMBER = 'CallerIDNum'
POSITION = 'Position'
QUEUE = 'Queue'
UNIQUE_ID = 'Uniqueid'
COUNT = 'Count'


def parse_join(event):
    try:
        manager = QueueEntryManager.get_instance()
        manager.join(event[QUEUE],
                     int(event[POSITION]),
                     int(event[COUNT]),
                     event[NAME],
                     event[NUMBER],
                     event[UNIQUE_ID])
    except Exception:
        logger.warning('Failed to parse Join event %s', event)


def parse_leave(event):
    try:
        manager = QueueEntryManager.get_instance()
        manager.leave(event[QUEUE],
                      int(event[POSITION]),
                      int(event[COUNT]),
                      event[UNIQUE_ID])
    except KeyError:
        logger.warning('Failed to parse Leave event %s', event)


class QueueEntryManager(object):

    _instance = None

    def __init__(self):
        self._queue_entries = {}

    def join(self, queue_name, pos, count, name, number, unique_id):
        try:
            entry = QueueEntry(pos, name, number)
            if queue_name not in self._queue_entries:
                self._queue_entries[queue_name] = {}
            self._queue_entries[queue_name][unique_id] = entry
            self._count_check(queue_name, count)
        except Exception:
            # Sync
            logger.exception('Failed to insert queue entry')

    def leave(self, queue_name, pos, count, unique_id):
        try:
            assert(self._queue_entries[queue_name][unique_id].position == pos)
            self._queue_entries[queue_name].pop(unique_id)
            self._decrement_position(queue_name, pos)
            self._count_check(queue_name, count)
        except Exception:
            # Sync
            logger.exception('Failed to remove queue entry')

    def _count_check(self, queue_name, expected_count):
        if queue_name in self._queue_entries:
            assert(expected_count == len(self._queue_entries[queue_name]))
        else:
            assert(expected_count == 0)

    def _decrement_position(self, queue_name, removed_position):
        try:
            for unique_id, entry in self._queue_entries[queue_name].iteritems():
                if entry.position > removed_position:
                    pos = entry.position - 1
                    assert(pos > 0)
                    new_entry = QueueEntry(pos, entry.name, entry.number)
                    self._queue_entries[queue_name][unique_id] = new_entry
        except Exception:
            # Sync
            logger.exception('Failed to decrement queue positions')

    @classmethod
    def get_instance(cls):
        if cls._instance == None:
            cls._instance = cls()
        return cls._instance
