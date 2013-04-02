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

import time
import logging

from xivo_cti import db_connection_manager, cti_config
from xivo_cti.ami import ami_callback_handler

logger = logging.getLogger('XiVO queue logger')

CALLERIDNUM = 'CallerIDNum'
CALLTIME = 'call_time_t'
HOLDTIME = 'HoldTime'
MEMBER = 'Member'
QUEUE = 'Queue'
TALKTIME = 'TalkTime'
UNIQUEID = 'Uniqueid'


class QueueLogger(object):
    _uri = None
    last_transaction = None
    cache = None
    cache_threshold = 10  # Time to wait in sec before removing from the
                            # from the cache when a call is not answered

    @classmethod
    def init(cls):
        cls.last_transaction = time.time()
        cls.cache = {}
        cls._register_ami_callbacks()

    @classmethod
    def _register_ami_callbacks(cls):
        ami_handler = ami_callback_handler.AMICallbackHandler.get_instance()
        ami_handler.register_callback('Join', cls.Join)
        ami_handler.register_callback('Leave', cls.Leave)
        ami_handler.register_callback('AgentConnect', cls.AgentConnect)
        ami_handler.register_callback('AgentComplete', cls.AgentComplete)

    @classmethod
    def _store_in_db(cls, sql):
        with db_connection_manager.DbConnectionPool(cti_config.DB_URI) as connection:
            connection['cur'].query(str(sql))
            connection['conn'].commit()

    @classmethod
    def _trace_event(cls, ev):
        queue = ev[QUEUE]
        if not queue in cls.cache:
            cls.cache[queue] = {}

        uniqueid = ev[UNIQUEID]
        if not uniqueid in cls.cache[queue]:
            cls.cache[queue][uniqueid] = ev
        else:
            cls.cache[queue][uniqueid] = dict(cls.cache[queue][uniqueid].items() + ev.items())

    @classmethod
    def _is_traced_event(cls, ev):
        queue = ev[QUEUE]
        return queue in cls.cache and ev[UNIQUEID] in cls.cache[queue]

    @classmethod
    def _show_cache(cls):
        count = 0
        for value in cls.cache.itervalues():
            count += len(value)
        logger.info('Cache size: %s\ncache = %s', count, cls.cache)

    @classmethod
    def _clean_cache(cls):
        '''If a call has left the queue for cache_threshold amount of time
        without being answered by an agent, we can remove it from the cache'''
        max_time = time.time() - cls.cache_threshold
        to_delete = []
        for queue, events in cls.cache.iteritems():
            for event, values in events.iteritems():
                if HOLDTIME not in values:
                    continue
                leave_time = values[CALLTIME] + int(values[HOLDTIME])
                if MEMBER not in values and leave_time < max_time:
                    to_delete.append((queue, event))
        for queue, event in to_delete:
            del cls.cache[queue][event]

    @classmethod
    def Join(cls, ev):
        ev[CALLTIME] = time.time()

        sql = '''INSERT INTO queue_info (call_time_t, queue_name, ''' \
                          '''caller, caller_uniqueid) ''' \
              '''VALUES (%d, '%s', '%s', '%s');''' % \
              (ev[CALLTIME], ev[QUEUE], ev[CALLERIDNUM], ev[UNIQUEID])

        cls._trace_event(ev)
        cls._store_in_db(sql)

    @classmethod
    def AgentConnect(cls, ev):
        if not cls._is_traced_event(ev):
            return ""

        ct = cls.cache[ev[QUEUE]][ev[UNIQUEID]][CALLTIME]

        sql = '''UPDATE queue_info '''\
              '''SET call_picker = '%s', hold_time = %s '''\
              '''WHERE call_time_t = %d and caller_uniqueid = '%s'; ''' % \
              (ev[MEMBER], ev[HOLDTIME], ct, ev[UNIQUEID])

        cls._trace_event(ev)
        cls._store_in_db(sql)

    @classmethod
    def AgentComplete(cls, ev):
        if not cls._is_traced_event(ev):
            return ""

        ct = cls.cache[ev[QUEUE]][ev[UNIQUEID]][CALLTIME]

        sql = '''UPDATE queue_info ''' \
              '''SET talk_time = %s ''' \
              '''WHERE call_time_t = %d and caller_uniqueid = '%s'; ''' % \
              (ev[TALKTIME], ct, ev[UNIQUEID])

        del cls.cache[ev[QUEUE]][ev[UNIQUEID]]

        cls._store_in_db(sql)

    @classmethod
    def Leave(cls, ev):
        if not cls._is_traced_event(ev):
            return ""

        ev[HOLDTIME] = time.time() - cls.cache[ev[QUEUE]][ev[UNIQUEID]][CALLTIME]
        ct = cls.cache[ev[QUEUE]][ev[UNIQUEID]][CALLTIME]

        sql = '''UPDATE queue_info ''' \
              '''SET hold_time = %d ''' \
              '''WHERE call_time_t = %d and caller_uniqueid = '%s'; ''' % \
              (ev[HOLDTIME], ct, ev[UNIQUEID])

        cls._trace_event(ev)
        cls._store_in_db(sql)

        # if the patch to get the reason is not applied, the cache is cleaned
        # manually
        if 'Reason' in ev:
            if ev['Reason'] == "0":
                del cls.cache[ev[QUEUE]][ev[UNIQUEID]]
        else:
            cls._clean_cache()
