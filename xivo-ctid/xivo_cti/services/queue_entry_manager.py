from collections import namedtuple

import time
import logging

logger = logging.getLogger(__name__)

QueueEntry = namedtuple('QueueEntry', ['position', 'name', 'number', 'join_time'])

NAME, NUMBER, POSITION, QUEUE, UNIQUE_ID, COUNT, WAIT = \
    'CallerIDName', 'CallerIDNum', 'Position', 'Queue', 'Uniqueid', 'Count', 'Wait'


def parse_join(event):
    try:
        manager = QueueEntryManager.get_instance()
        manager.join(event[QUEUE],
                     int(event[POSITION]),
                     int(event[COUNT]),
                     event[NAME],
                     event[NUMBER],
                     event[UNIQUE_ID])
    except (KeyError, ValueError):
        logger.warning('Failed to parse Join event %s', event)


def parse_queue_entry(event):
    try:
        manager = QueueEntryManager.get_instance()
        manager.insert(event[QUEUE],
                       int(event[POSITION]),
                       event[NAME],
                       event[NUMBER],
                       event[UNIQUE_ID],
                       int(event[WAIT]))
    except (KeyError, ValueError):
        logger.warning('Failed to parse QueueEntry event %s', event)


def parse_leave(event):
    try:
        manager = QueueEntryManager.get_instance()
        manager.leave(event[QUEUE],
                      int(event[POSITION]),
                      int(event[COUNT]),
                      event[UNIQUE_ID])
    except (KeyError, ValueError):
        logger.warning('Failed to parse Leave event %s', event)


def parse_queue_params(event):
    try:
        manager = QueueEntryManager.get_instance()
        manager.clear_data(event[QUEUE])
    except KeyError:
        logger.warning('Failed to parse QueueParams event %s', event)


class QueueEntryManager(object):

    _instance = None

    def __init__(self):
        self._queue_entries = {}
        self._ami = None

    def join(self, queue_name, pos, count, name, number, unique_id):
        try:
            self.insert(queue_name, pos, name, number, unique_id, 0)
            self._count_check(queue_name, count)
        except Exception:
            self.synchronize(queue_name)
            logger.exception('Failed to insert queue entry')

    def insert(self, queue_name, pos, name, number, unique_id, wait):
        try:
            entry = QueueEntry(pos, name, number, time.time() - wait)
            if queue_name not in self._queue_entries:
                self._queue_entries[queue_name] = {}
            self._queue_entries[queue_name][unique_id] = entry
        except Exception:
            logger.exception('Failed to insert queue entry')

    def leave(self, queue_name, pos, count, unique_id):
        try:
            assert(self._queue_entries[queue_name][unique_id].position == pos)
            self._queue_entries[queue_name].pop(unique_id)
            self._decrement_position(queue_name, pos)
            self._count_check(queue_name, count)
        except Exception:
            self.synchronize(queue_name)
            logger.exception('Failed to remove queue entry')

    def synchronize(self, queue_name=None):
        logger.info('Synchronizing QueueMemberEntry on %s',
                    (queue_name if queue_name else 'all queues'))
        if self._ami != None:
            self._ami.sendqueuestatus(queue_name)
        else:
            logger.warning('QueueEntryManager cannot contact any AMI instance')

    def clear_data(self, queue_name):
        self._queue_entries.pop(queue_name, None)

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
                    new_entry = QueueEntry(pos,
                                           entry.name,
                                           entry.number,
                                           entry.join_time)
                    self._queue_entries[queue_name][unique_id] = new_entry
        except Exception:
            # Sync
            logger.exception('Failed to decrement queue positions')

    @classmethod
    def get_instance(cls):
        if cls._instance == None:
            cls._instance = cls()
        return cls._instance
