class StatisticsProducerInitializer:

    def __init__(self, queue_service_manager, queuemember_service_manager):
        self.queue_service_manager = queue_service_manager
        self.queuemember_service_manager = queuemember_service_manager

    def init_queue_statistics_producer(self, queue_statistics_producer):
        queue_names = self.queue_service_manager.get_queue_names()
        for queue_name in queue_names:
            queue_statistics_producer.on_queue_added(queue_name)
        queuemember_ids = self.queuemember_service_manager.get_queuemember_ids()
        for (queue_id, agent_id) in queuemember_ids:
            queue_statistics_producer.on_agent_added(queue_id, agent_id)
