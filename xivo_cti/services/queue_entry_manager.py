# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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

from collections import namedtuple

from xivo_dao.helpers.db_utils import session_scope
from xivo_dao import queue_dao

from xivo_cti import dao
from xivo_cti.ioc.context import context
from xivo_cti.ami.ami_callback_handler import AMICallbackHandler

import time
import logging

logger = logging.getLogger(__name__)

QueueEntry = namedtuple('QueueEntry', ['position', 'name', 'number', 'join_time', 'unique_id'])

NAME, NUMBER, POSITION, QUEUE, UNIQUE_ID, COUNT, WAIT = \
    'CallerIDName', 'CallerIDNum', 'Position', 'Queue', 'Uniqueid', 'Count', 'Wait'


def register_events():
    callback_handler = AMICallbackHandler.get_instance()
    callback_handler.register_callback('QueueCallerJoin', parse_join)
    callback_handler.register_callback('QueueCallerLeave', parse_leave)
    callback_handler.register_callback('QueueEntry', parse_queue_entry)
    callback_handler.register_callback('QueueParams', parse_queue_params)
    callback_handler.register_callback('QueueStatusComplete', parse_queue_status_complete)


def parse_join(event):
    try:
        manager = context.get('queue_entry_manager')
        manager.join(event[QUEUE],
                     int(event[POSITION]),
                     int(event[COUNT]),
                     event[NAME],
                     event[NUMBER],
                     event[UNIQUE_ID])
    except (KeyError, ValueError):
        logger.warning('Failed to parse QueueCallerJoin event %s', event)


def parse_queue_entry(event):
    try:
        manager = context.get('queue_entry_manager')
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
        manager = context.get('queue_entry_manager')
        manager.leave(event[QUEUE],
                      int(event[POSITION]),
                      int(event[COUNT]),
                      event[UNIQUE_ID])
    except (KeyError, ValueError):
        logger.warning('Failed to parse QueueCallerLeave event %s', event)


def parse_queue_params(event):
    try:
        manager = context.get('queue_entry_manager')
        manager.clear_data(event[QUEUE])
    except KeyError:
        logger.warning('Failed to parse QueueParams event %s', event)


def parse_queue_status_complete(event):
    manager = context.get('queue_entry_manager')
    manager.publish()


def longest_wait_time_calculator(queue_infos):
    call_entry_time = time.time()
    for call in queue_infos:
        if queue_infos[call].join_time < call_entry_time:
            call_entry_time = queue_infos[call].join_time
    return time.time() - call_entry_time


class QueueEntryManager(object):

    def __init__(self,
                 queue_entry_notifier,
                 queue_entry_encoder,
                 statistics_notifier,
                 ami_class):
        self._queue_entries = {}
        self._notifier = queue_entry_notifier
        self._encoder = queue_entry_encoder
        self._statistics_notifier = statistics_notifier
        self._ami = ami_class

    def join(self, queue_name, pos, count, name, number, unique_id):
        if not dao.queue.exists(queue_name):
            return
        try:
            self.insert(queue_name, pos, name, number, unique_id, 0)
            self._count_check(queue_name, count)
        except (LookupError, AssertionError):
            self.synchronize(queue_name)
            logger.exception('Failed to insert queue entry')
        else:
            self.publish(queue_name)
            self.publish_realtime_stats(queue_name)

    def insert(self, queue_name, pos, name, number, unique_id, wait):
        logger.info("queue %s pos %s name %s number %s wait %s" % (queue_name, pos, name, number, wait))
        try:
            entry = QueueEntry(pos, name, number, time.time() - wait, unique_id)
            if queue_name not in self._queue_entries:
                self._queue_entries[queue_name] = {}
            self._queue_entries[queue_name][unique_id] = entry
        except LookupError:
            logger.exception('Failed to insert queue entry')

    def leave(self, queue_name, pos, count, unique_id):
        if not dao.queue.exists(queue_name):
            return
        try:
            assert(self._queue_entries[queue_name][unique_id].position == pos)
            self._queue_entries[queue_name].pop(unique_id)
            self._decrement_position(queue_name, pos)
            self._count_check(queue_name, count)
        except (LookupError, AssertionError):
            self.synchronize(queue_name)
            logger.exception('Failed to remove queue entry')
        else:
            self.publish(queue_name)
            self.publish_realtime_stats(queue_name)

    def synchronize(self, queue_name=None):
        logger.info('Synchronizing QueueEntries on %s',
                    (queue_name if queue_name else 'all queues'))
        if self._ami is not None:
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
                    new_entry = QueueEntry(
                        pos,
                        entry.name,
                        entry.number,
                        entry.join_time,
                        unique_id
                    )
                    self._queue_entries[queue_name][unique_id] = new_entry
        except (LookupError, AssertionError):
            logger.exception('Failed to decrement queue positions')
            self.synchronize(queue_name)

    def publish(self, queue_name=None):
        if queue_name and queue_name in self._queue_entries:
            encoded_status = self._encoder.encode(queue_name,
                                                  self._queue_entries[queue_name])
            logger.info('Publishing entries for %s: %s', queue_name, encoded_status)
            self._notifier.publish(queue_name, encoded_status)
        elif queue_name is None:
            for q in self._queue_entries.keys():
                self.publish(q)

    def publish_realtime_stats(self, queue_name):
        self._statistics_notifier.on_stat_changed(self._encode_stats(queue_name))

    def publish_all_realtime_stats(self, cti_connection):
        queues_to_remove = set()
        for queue_name in self._queue_entries:
            try:
                self._statistics_notifier.send_statistic(self._encode_stats(queue_name), cti_connection)
            except LookupError:
                queues_to_remove.add(queue_name)
                logger.info("queue : %s does not exists ", queue_name)
        self._remove_queues(queues_to_remove)

    def _remove_queues(self, queues_to_remove):
        for queue_name in queues_to_remove:
            self._queue_entries.pop(queue_name)

    def _encode_stats(self, queue_name):
        with session_scope():
            queue_id = queue_dao.id_from_name(queue_name)
        realtime_stat = {'%s' % queue_id: {u'Xivo-WaitingCalls': len(self._queue_entries[queue_name])}}
        if len(self._queue_entries[queue_name]) >= 1:
            longest_wait_time = longest_wait_time_calculator(self._queue_entries[queue_name])
            logger.info('for queue %s longest wait time %s' % (queue_name, longest_wait_time))
            realtime_stat["%s" % queue_id][u'Xivo-LongestWaitTime'] = long(longest_wait_time)
        return realtime_stat
