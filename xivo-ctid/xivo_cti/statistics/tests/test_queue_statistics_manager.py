# -*- coding: utf-8 -*-

import unittest
from xivo_cti.statistics import queue_statistics_manager
from xivo_cti.statistics.queue_statistics_manager import QueueStatisticsManager
from tests.mock import Mock
from xivo_cti.dao.queuestatisticdao import QueueStatisticDAO
from xivo_cti.xivo_ami import AMIClass
from xivo_cti.tools.delta_computer import DictDelta

class Test(unittest.TestCase):

    def setUp(self):
        self.queue_statistic_dao = Mock(QueueStatisticDAO)
        self.queue_statistics_manager = QueueStatisticsManager.get_instance()
        self.queue_statistics_manager._queue_statistic_dao = self.queue_statistic_dao

    def tearDown(self):
        QueueStatisticsManager._instance = None

    def test_getStatistics(self):
        window = 3600
        xqos = 25
        self.queue_statistic_dao.get_received_call_count.return_value = 7
        self.queue_statistic_dao.get_answered_call_count.return_value = 12
        self.queue_statistic_dao.get_abandonned_call_count.return_value = 11
        self.queue_statistic_dao.get_answered_call_in_qos_count.return_value = 0
        self.queue_statistic_dao.get_received_and_done.return_value = 11
        self.queue_statistic_dao.get_max_hold_time.return_value = 120

        queue_statistics = self.queue_statistics_manager.get_statistics('3', xqos, window)


        self.assertEqual(queue_statistics.received_call_count, 7)
        self.assertEqual(queue_statistics.answered_call_count, 12)
        self.assertEqual(queue_statistics.abandonned_call_count, 11)
        self.assertEqual(queue_statistics.max_hold_time, 120)
        self.queue_statistic_dao.get_received_call_count.assert_called_with('3', window)
        self.queue_statistic_dao.get_answered_call_count.assert_called_with('3', window)
        self.queue_statistic_dao.get_abandonned_call_count.assert_called_with('3', window)
        self.queue_statistic_dao.get_max_hold_time.assert_called_with('3', window)

    def test_calculate_efficiency(self):
        window = 3600
        xqos = 25
        self.queue_statistic_dao.get_received_call_count.return_value = 18
        self.queue_statistic_dao.get_answered_call_count.return_value = 3
        self.queue_statistic_dao.get_answered_call_in_qos_count.return_value = 0
        self.queue_statistic_dao.get_received_and_done.return_value = 11


        queue_statistics = self.queue_statistics_manager.get_statistics('3', xqos, window)

        self.assertEqual(queue_statistics.efficiency, 27)


    def test_efficiency_no_call_received_and_done(self):
        window = 3600
        xqos = 25
        self.queue_statistic_dao.get_received_call_count.return_value = 3
        self.queue_statistic_dao.get_answered_call_count.return_value = 0
        self.queue_statistic_dao.get_answered_call_in_qos_count.return_value = 0
        self.queue_statistic_dao.get_received_and_done.return_value = 0

        queue_statistics = self.queue_statistics_manager.get_statistics('3', xqos, window)

        self.assertEqual(queue_statistics.efficiency, None)

    def test_qos(self):
        window = 3600
        xqos = 25
        self.queue_statistic_dao.get_answered_call_count.return_value = 11
        self.queue_statistic_dao.get_answered_call_in_qos_count.return_value = 3
        self.queue_statistic_dao.get_received_call_count.return_value = 50
        self.queue_statistic_dao.get_received_and_done.return_value = 11

        queue_statistics = self.queue_statistics_manager.get_statistics('3', xqos, window)

        self.assertEqual(queue_statistics.qos, 27)

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


        input_delta = DictDelta({'Agent/2345,service':
                                    {'queue_name':'service', 'interface':'Agent/2345'},
                                 'Agent/2309,beans':
                                    {'queue_name':'beans', 'interface':'Agent/2309'}
                                 }, {}, {})

        queue_statistics_manager.parse_queue_member_update(input_delta)

        self.queue_statistics_manager.get_queue_summary.assert_was_called_with('service')
        self.queue_statistics_manager.get_queue_summary.assert_was_called_with('beans')

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
