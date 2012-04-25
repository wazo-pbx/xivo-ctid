'''
Created on 2012-04-24

@author: jylebleu
'''
import unittest
from xivo_cti.services.queue_service_manager import QueueServiceManager
from xivo_cti.statistics.queuestatisticsproducer import QueueStatisticsProducer
from tests.mock import Mock
from xivo_cti.statistics.statistics_producer_initializer import StatisticsProducerInitializer
from xivo_cti.services.queuemember_service_manager import QueueMemberServiceManager


class TestStatisticsProducerInitializer(unittest.TestCase):


    def setUp(self):
        self.queue_service_manager = Mock(QueueServiceManager)
        self.queuemember_service_manager = Mock(QueueMemberServiceManager)
        self.queue_statistics_producer = Mock(QueueStatisticsProducer)
        self.statistics_producer_initializer = StatisticsProducerInitializer(self.queue_service_manager, self.queuemember_service_manager)


    def tearDown(self):
        pass


    def test_init_queue_statistics_producer_queues(self):
        self.queuemember_service_manager.get_queuemember_ids.return_value = []

        self.queue_service_manager.get_queue_ids.return_value = ['1', '2']

        self.statistics_producer_initializer.init_queue_statistics_producer(self.queue_statistics_producer)

        self.queue_service_manager.get_queue_ids.assert_called_once_with()
        self.queue_statistics_producer.on_queue_added.assert_was_called_with('1')
        self.queue_statistics_producer.on_queue_added.assert_was_called_with('2')

    def test_init_queue_statistics_producer_members(self):

        self.queuemember_service_manager.get_queuemember_ids.return_value = [('1', '50'), ('2', '24')]
        self.queue_service_manager.get_queue_ids.return_value = []

        self.statistics_producer_initializer.init_queue_statistics_producer(self.queue_statistics_producer)

        self.queuemember_service_manager.get_queuemember_ids.assert_called_once_with()
        self.queue_statistics_producer.on_agent_added.assert_was_called_with('1', '50')
        self.queue_statistics_producer.on_agent_added.assert_was_called_with('2', '24')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_create_queue_statistics_producer_factory']
    unittest.main()
