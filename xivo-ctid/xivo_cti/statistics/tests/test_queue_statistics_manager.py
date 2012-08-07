# -*- coding: utf-8 -*-

import unittest
import time
from xivo_cti.statistics import queue_statistics_manager
from xivo_cti.statistics.queue_statistics_manager import QueueStatisticsManager,\
    CachingQueueStatisticsManagerDecorator
from tests.mock import Mock, patch
from xivo_dao.queuestatisticdao import QueueStatisticDAO
from xivo_cti.xivo_ami import AMIClass
from xivo_cti.tools.delta_computer import DictDelta
from xivo_cti.model.queuestatistic import NO_VALUE


class TestQueueStatisticsManager(unittest.TestCase):

    def setUp(self):
        self.queue_statistic_dao = Mock(QueueStatisticDAO)
        QueueStatisticsManager._instance = QueueStatisticsManager()
        self.queue_statistics_manager = QueueStatisticsManager.get_instance()
        self.queue_statistics_manager._queue_statistic_dao = self.queue_statistic_dao

    def tearDown(self):
        QueueStatisticsManager._instance = None

    def test_getStatistics(self):
        window = 3600
        xqos = 25
        dao_queue_statistic = Mock()
        dao_queue_statistic.received_call_count = 7
        dao_queue_statistic.answered_call_count = 12
        dao_queue_statistic.answered_call_in_qos_count = 0
        dao_queue_statistic.abandonned_call_count = 11
        dao_queue_statistic.received_and_done = 11
        dao_queue_statistic.max_hold_time = 120
        dao_queue_statistic.mean_hold_time = 15
        self.queue_statistic_dao.get_statistics.return_value = dao_queue_statistic

        queue_statistics = self.queue_statistics_manager.get_statistics('3', xqos, window)

        self.assertEqual(queue_statistics.received_call_count, 7)
        self.assertEqual(queue_statistics.answered_call_count, 12)
        self.assertEqual(queue_statistics.abandonned_call_count, 11)
        self.assertEqual(queue_statistics.max_hold_time, 120)
        self.assertEqual(queue_statistics.mean_hold_time, 15)
        self.queue_statistic_dao.get_statistics.assert_called_with('3', window, xqos)

    def test_calculate_efficiency_round_down(self):
        window = 3600
        xqos = 25
        dao_queue_statistic = Mock()
        dao_queue_statistic.received_call_count = 18
        dao_queue_statistic.answered_call_count = 3
        dao_queue_statistic.answered_call_in_qos_count = 0
        dao_queue_statistic.received_and_done = 11
        self.queue_statistic_dao.get_statistics.return_value = dao_queue_statistic

        queue_statistics = self.queue_statistics_manager.get_statistics('3', xqos, window)

        self.assertEqual(queue_statistics.efficiency, 27)

    def test_calculate_efficiency_round_up(self):
        window = 3600
        xqos = 25
        dao_queue_statistic = Mock()
        dao_queue_statistic.received_call_count = 18
        dao_queue_statistic.answered_call_count = 12
        dao_queue_statistic.answered_call_in_qos_count = 0
        dao_queue_statistic.received_and_done = 14
        self.queue_statistic_dao.get_statistics.return_value = dao_queue_statistic

        queue_statistics = self.queue_statistics_manager.get_statistics('3', xqos, window)

        self.assertEqual(queue_statistics.efficiency, 86)

    def test_efficiency_no_call_received_and_done(self):
        window = 3600
        xqos = 25
        dao_queue_statistic = Mock()
        dao_queue_statistic.received_call_count = 3
        dao_queue_statistic.answered_call_count = 0
        dao_queue_statistic.answered_call_in_qos_count = 0
        dao_queue_statistic.received_and_done = 0
        self.queue_statistic_dao.get_statistics.return_value = dao_queue_statistic

        queue_statistics = self.queue_statistics_manager.get_statistics('3', xqos, window)

        self.assertEqual(queue_statistics.efficiency, NO_VALUE)

    def test_qos_no_answered_calls_in_period(self):
        window = 3600
        xqos = 25
        dao_queue_statistic = Mock()
        dao_queue_statistic.answered_call_count = 0
        self.queue_statistic_dao.get_statistics.return_value = dao_queue_statistic

        queue_statistics = self.queue_statistics_manager.get_statistics('3', xqos, window)

        self.assertEqual(queue_statistics.qos, NO_VALUE)
        self.assertEqual(queue_statistics.efficiency, NO_VALUE)

    def test_qos_round_down(self):
        window = 3600
        xqos = 25
        dao_queue_statistic = Mock()
        dao_queue_statistic.received_call_count = 50
        dao_queue_statistic.answered_call_count = 11
        dao_queue_statistic.answered_call_in_qos_count = 3
        dao_queue_statistic.received_and_done = 11
        self.queue_statistic_dao.get_statistics.return_value = dao_queue_statistic

        queue_statistics = self.queue_statistics_manager.get_statistics('3', xqos, window)

        self.assertEqual(queue_statistics.qos, 27)

    def test_qos_round_up(self):
        window = 3600
        xqos = 25
        dao_queue_statistic = Mock()
        dao_queue_statistic.received_call_count = 50
        dao_queue_statistic.answered_call_count = 14
        dao_queue_statistic.answered_call_in_qos_count = 12
        dao_queue_statistic.received_and_done = 14
        self.queue_statistic_dao.get_statistics.return_value = dao_queue_statistic

        queue_statistics = self.queue_statistics_manager.get_statistics('3', xqos, window)

        self.assertEqual(queue_statistics.qos, 86)

    def test_parse_queue_member_status(self):
        self.queue_statistics_manager.get_queue_summary = Mock()
        queue_name = 'services'
        queuememberstatus_event = {'Event': 'QueueMemberStatus',
                                   'Queue': queue_name,
                                   'Interface': 'Agent/4523'}

        queue_statistics_manager.parse_queue_member_status(queuememberstatus_event)

        self.queue_statistics_manager.get_queue_summary.assert_called_once_with(queue_name)

    def test_parse_queue_member_update(self):
        self.queue_statistics_manager.get_queue_summary = Mock()

        input_delta = DictDelta({'Agent/2345,service': {'queue_name': 'service',
                                                        'interface': 'Agent/2345'},
                                 'Agent/2309,beans': {'queue_name': 'beans',
                                                      'interface': 'Agent/2309'}
                                 }, {}, {})

        queue_statistics_manager.parse_queue_member_update(input_delta)

        self.queue_statistics_manager.get_queue_summary.assert_was_called_with('service')
        self.queue_statistics_manager.get_queue_summary.assert_was_called_with('beans')

    @patch('xivo_dao.queue_features_dao.is_a_queue', Mock())
    def test_get_queue_summary(self):
        queue_name = 'services'

        self.ami_wrapper = Mock(AMIClass)
        self.queue_statistics_manager.ami_wrapper = self.ami_wrapper

        self.queue_statistics_manager.get_queue_summary(queue_name)

        self.ami_wrapper.queuesummary.assert_called_once_with(queue_name)

    def test_get_all_queue_summary(self):
        self.ami_wrapper = Mock(AMIClass)
        self.queue_statistics_manager.ami_wrapper = self.ami_wrapper

        self.queue_statistics_manager.get_all_queue_summary()

        self.ami_wrapper.queuesummary.assert_called_once_with()


class TestCachingQueueStatisticsManagerDecorator(unittest.TestCase):

    def test_get_statistics_return_cached_result_if_inside_time(self):
        queue_stats_mgr = self._new_caching_queue_stats_mgr(1.0)

        queue_stats_mgr._queue_stats_mgr.get_statistics.return_value = 1
        result = queue_stats_mgr.get_statistics('foo', 15, 3600)
        self.assertEqual(1, result)

        queue_stats_mgr._queue_stats_mgr.get_statistics.return_value = 2
        result = queue_stats_mgr.get_statistics('foo', 15, 3600)
        self.assertEqual(1, result)

    def test_get_statistics_return_fresh_result_if_outside_time(self):
        queue_stats_mgr = self._new_caching_queue_stats_mgr(0.1)

        queue_stats_mgr._queue_stats_mgr.get_statistics.return_value = 1
        result = queue_stats_mgr.get_statistics('foo', 15, 3600)
        self.assertEqual(1, result)

        time.sleep(0.2)
        queue_stats_mgr._queue_stats_mgr.get_statistics.return_value = 2
        result = queue_stats_mgr.get_statistics('foo', 15, 3600)
        self.assertEqual(2, result)

    def _new_caching_queue_stats_mgr(self, caching_time):
        return CachingQueueStatisticsManagerDecorator(Mock(), caching_time)
