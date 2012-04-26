class StatisticsProducerInitializer:

    def __init__(self, queue_service_manager):
        self.queue_service_manager = queue_service_manager

    def init_queue_statistics_producer(self, queue_statistics_producer):
        queue_ids = self.queue_service_manager.get_queue_ids()
        for queue_id in queue_ids:
            queue_statistics_producer.on_queue_added(queue_id)
