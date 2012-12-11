# -*- coding: utf-8 -*-

import logging
import time
from xivo_dao import queue_features_dao, queue_statistic_dao
from xivo_cti.context import context
from xivo_cti.model.queuestatistic import QueueStatistic
from xivo_cti.ami.ami_callback_handler import AMICallbackHandler

logger = logging.getLogger("QueueStatisticsManager")


def register_events():
    callback_handler = AMICallbackHandler.get_instance()
    callback_handler.register_callback('QueueMemberStatus', parse_queue_member_status)
    callback_handler.register_callback('QueueMemberAdded', parse_queue_member_status)
    callback_handler.register_callback('QueueMemberRemoved', parse_queue_member_status)
    callback_handler.register_callback('QueueMemberPaused', parse_queue_member_status)

    queue_member_callback_handler = context.get('queuemember_service_notifier')
    queue_member_callback_handler.subscribe(parse_queue_member_update)


def parse_queue_member_status(event):
    try:
        manager = context.get('queue_statistics_manager')
        manager.get_queue_summary(event['Queue'])
    except (KeyError, ValueError):
        logger.warning('Failed to parse QueueSummary event %s', event)


def parse_queue_member_update(delta):
    manager = context.get('queue_statistics_manager')
    for queue_members in (delta.add, delta.change, delta.delete):
        for queue_member in queue_members.itervalues():
            manager.get_queue_summary(queue_member['queue_name'])


class QueueStatisticsManager(object):

    def __init__(self, ami_class):
        self.ami_wrapper = ami_class

    def get_statistics(self, queue_name, xqos, window):
        dao_queue_statistic = queue_statistic_dao.get_statistics(queue_name, window, xqos)

        queue_statistic = QueueStatistic()
        queue_statistic.received_call_count = dao_queue_statistic.received_call_count
        queue_statistic.answered_call_count = dao_queue_statistic.answered_call_count
        queue_statistic.abandonned_call_count = dao_queue_statistic.abandonned_call_count
        if dao_queue_statistic.max_hold_time is None:
            queue_statistic.max_hold_time = ''
        else:
            queue_statistic.max_hold_time = dao_queue_statistic.max_hold_time
        if dao_queue_statistic.mean_hold_time is None:
            queue_statistic.mean_hold_time = ''
        else:
            queue_statistic.mean_hold_time = dao_queue_statistic.mean_hold_time

        if queue_statistic.answered_call_count:
            received_and_done = dao_queue_statistic.received_and_done
            if received_and_done:
                queue_statistic.efficiency = int(round((float(queue_statistic.answered_call_count) / received_and_done * 100)))

            answered_in_qos = dao_queue_statistic.answered_call_in_qos_count
            queue_statistic.qos = int(round(float(answered_in_qos) / queue_statistic.answered_call_count * 100))
        return queue_statistic

    def get_queue_summary(self, queue_name):
        if queue_features_dao.is_a_queue(queue_name):
            self.ami_wrapper.queuesummary(queue_name)

    def get_all_queue_summary(self):
        self.ami_wrapper.queuesummary()


class CachingQueueStatisticsManagerDecorator(object):

    _DEFAULT_CACHING_TIME = 5

    def __init__(self, queue_stats_mgr, caching_time=None):
        self._queue_stats_mgr = queue_stats_mgr
        self._caching_time = self._compute_caching_time(caching_time)
        self._cache = {}

    def _compute_caching_time(self, caching_time):
        if caching_time is None:
            return self._DEFAULT_CACHING_TIME
        else:
            return caching_time

    def get_statistics(self, queue_name, xqos, window):
        current_time = time.time()
        cache_key = (queue_name, xqos, window)
        if cache_key in self._cache:
            cache_time, cache_value = self._cache[cache_key]
            if cache_time + self._caching_time > current_time:
                return cache_value
        new_value = self._queue_stats_mgr.get_statistics(queue_name, xqos, window)
        self._cache[cache_key] = (current_time, new_value)
        return new_value

    def __getattr__(self, name):
        return getattr(self._queue_stats_mgr, name)

    @property
    def ami_wrapper(self):
        return self._queue_stats_mgr.ami_wrapper

    @ami_wrapper.setter
    def ami_wrapper(self, value):
        self._queue_stats_mgr.ami_wrapper = value
