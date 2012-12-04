# -*- coding: utf-8 -*-

import unittest
from tests.mock import Mock
from xivo_cti.services.queue_service_manager import QueueServiceManager
from xivo_cti.statistics.queue_statistics_producer import QueueStatisticsProducer
from xivo_cti.statistics.statistics_producer_initializer import StatisticsProducerInitializer


class TestStatisticsProducerInitializer(unittest.TestCase):

    def setUp(self):
        self.agent_client = Mock()
        self.queue_service_manager = Mock(QueueServiceManager)
        self.queue_statistics_producer = Mock(QueueStatisticsProducer)
        self.statistics_producer_initializer = StatisticsProducerInitializer(self.queue_service_manager, self.agent_client)

    def test_init_queue_statistics_producer_queues(self):
        self.agent_client.get_agent_statuses.return_value = []
        self.queue_service_manager.get_queue_ids.return_value = ['12', '24']

        self.statistics_producer_initializer.init_queue_statistics_producer(self.queue_statistics_producer)

        self.queue_service_manager.get_queue_ids.assert_called_once_with()
        self.queue_statistics_producer.on_queue_added.assert_was_called_with('12')
        self.queue_statistics_producer.on_queue_added.assert_was_called_with('24')

    def test_init_queue_statistics_producer_agents(self):
        self.agent_client.get_agent_statuses.return_value = [
            self._new_agent_status('123', True),
            self._new_agent_status('234', False),
        ]
        self.queue_service_manager.get_queue_ids.return_value = []

        self.statistics_producer_initializer.init_queue_statistics_producer(self.queue_statistics_producer)

        self.agent_client.get_agent_statuses.assert_called_once_with()
        self.queue_statistics_producer.on_agent_loggedon.assert_called_once_with('Agent/123')

    def _new_agent_status(self, agent_number, logged):
        agent_status = Mock()
        agent_status.number = agent_number
        agent_status.logged = logged
        return agent_status
