import unittest
from xivo_cti.services.queue_service_manager import QueueServiceManager
from xivo_cti.statistics.queue_statistics_producer import QueueStatisticsProducer
from tests.mock import Mock
from xivo_cti.statistics.statistics_producer_initializer import StatisticsProducerInitializer


class TestStatisticsProducerInitializer(unittest.TestCase):


    def setUp(self):
        self.queue_service_manager = Mock(QueueServiceManager)
        self.queue_statistics_producer = Mock(QueueStatisticsProducer)
        self.statistics_producer_initializer = StatisticsProducerInitializer(self.queue_service_manager)


    def tearDown(self):
        pass

    def test_init_queue_statistics_producer_queues(self):
        self.queue_service_manager.get_queue_ids.return_value = ['12', '24']

        self.statistics_producer_initializer.init_queue_statistics_producer(self.queue_statistics_producer)

        self.queue_service_manager.get_queue_ids.assert_called_once_with()
        self.queue_statistics_producer.on_queue_added.assert_was_called_with('12')
        self.queue_statistics_producer.on_queue_added.assert_was_called_with('24')
