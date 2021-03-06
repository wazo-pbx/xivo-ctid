# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import time
import logging

from xivo_cti.ami import ami_callback_handler

from xivo_dao.helpers.db_utils import session_scope
from xivo_dao import queue_info_dao

logger = logging.getLogger('XiVO queue logger')

CALLERIDNUM = 'CallerIDNum'
CALLTIME = 'call_time_t'
HOLDTIME = 'HoldTime'
INTERFACE = 'Interface'
QUEUE = 'Queue'
TALKTIME = 'TalkTime'
UNIQUEID = 'Uniqueid'


class QueueLogger(object):

    cache = None

    # Time to wait in sec before removing from the cache when a call is not answered
    cache_threshold = 10

    @classmethod
    def init(cls):
        cls.cache = {}
        cls._register_ami_callbacks()

    @classmethod
    def _register_ami_callbacks(cls):
        ami_handler = ami_callback_handler.AMICallbackHandler.get_instance()
        ami_handler.register_callback('QueueCallerJoin', cls.QueueCallerJoin)
        ami_handler.register_callback('QueueCallerLeave', cls.QueueCallerLeave)
        ami_handler.register_callback('AgentConnect', cls.AgentConnect)
        ami_handler.register_callback('AgentComplete', cls.AgentComplete)

    @classmethod
    def _trace_event(cls, ev):
        queue = ev[QUEUE]
        if queue not in cls.cache:
            cls.cache[queue] = {}

        uniqueid = ev[UNIQUEID]
        if uniqueid not in cls.cache[queue]:
            cls.cache[queue][uniqueid] = ev
        else:
            cls.cache[queue][uniqueid] = dict(cls.cache[queue][uniqueid].items() + ev.items())

    @classmethod
    def _is_traced_event(cls, ev):
        queue = ev[QUEUE]
        return queue in cls.cache and ev[UNIQUEID] in cls.cache[queue]

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
                if INTERFACE not in values and leave_time < max_time:
                    to_delete.append((queue, event))
        for queue, event in to_delete:
            del cls.cache[queue][event]

    @classmethod
    def QueueCallerJoin(cls, ev):
        ev[CALLTIME] = int(time.time())

        cls._trace_event(ev)

        with session_scope():
            queue_info_dao.add_entry(ev[CALLTIME], ev[QUEUE], ev[CALLERIDNUM], ev[UNIQUEID])

    @classmethod
    def AgentConnect(cls, ev):
        if not cls._is_traced_event(ev):
            return

        ct = cls.cache[ev[QUEUE]][ev[UNIQUEID]][CALLTIME]

        cls._trace_event(ev)

        with session_scope():
            queue_info_dao.update_holdtime(ev[UNIQUEID], ct, ev[HOLDTIME], ev[INTERFACE])

    @classmethod
    def AgentComplete(cls, ev):
        if not cls._is_traced_event(ev):
            return

        ct = cls.cache[ev[QUEUE]][ev[UNIQUEID]][CALLTIME]

        del cls.cache[ev[QUEUE]][ev[UNIQUEID]]

        with session_scope():
            queue_info_dao.update_talktime(ev[UNIQUEID], ct, ev[TALKTIME])

    @classmethod
    def QueueCallerLeave(cls, ev):
        if not cls._is_traced_event(ev):
            return

        ev[HOLDTIME] = int(time.time()) - cls.cache[ev[QUEUE]][ev[UNIQUEID]][CALLTIME]
        ct = cls.cache[ev[QUEUE]][ev[UNIQUEID]][CALLTIME]

        cls._trace_event(ev)

        with session_scope():
            queue_info_dao.update_holdtime(ev[UNIQUEID], ct, ev[HOLDTIME])

        cls._clean_cache()
