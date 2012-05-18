import logging
from collections import namedtuple
from xivo_cti.ami.ami_callback_handler import AMICallbackHandler
from xivo_cti.services.queue_service_manager import QueueServiceManager
from xivo_cti.services.queue_service_manager import NotAQueueException

logger = logging.getLogger("QueueStatisticsProducer")
QueueCounters = namedtuple('QueueCounters', ['available'])

def register_events():
    callback_handler = AMICallbackHandler.get_instance()
    callback_handler.register_callback('QueueSummary', parse_queue_summary)
    callback_handler.register_callback('AgentCalled', parse_agent_called)
    callback_handler.register_callback('AgentComplete', parse_agent_complete)


def parse_queue_summary(queuesummary_event):
    queue_name = queuesummary_event['Queue']
    counters = QueueCounters(available=queuesummary_event['Available'])

    queue_statistics_producer = QueueStatisticsProducer.get_instance()
    queue_service_manager = QueueServiceManager.get_instance()
    try:
        queue_id = queue_service_manager.get_queue_id(queue_name)
        queue_statistics_producer.on_queue_summary(queue_id, counters)
    except NotAQueueException:
        pass

def parse_agent_called(agentcalled_event):
    queue_statistics_producer = QueueStatisticsProducer.get_instance()

    agent_id = agentcalled_event['AgentCalled']
    queue_statistics_producer.on_agent_called(agent_id)


def parse_agent_complete(agentcomplete_event):
    pass

class QueueStatisticsProducer(object):

    LOGGEDAGENT_STATNAME = "Xivo-LoggedAgents"

    _instance = None

    def __init__(self):
        self.queues_of_agent = {}
        self.logged_agents = set()
        self.queues = set()

    def set_notifier(self, notifier):
        self.notifier = notifier

    def on_queue_added(self, queueid):
        self.queues.add(queueid)
        self._notify_change(queueid)

    def on_agent_added(self, queueid, agentid):
        if agentid not in self.queues_of_agent:
            self.queues_of_agent[agentid] = set()
        self.queues_of_agent[agentid].add(queueid)
        self._notify_change(queueid)

    def on_agent_loggedon(self, agentid):
        self.logged_agents.add(agentid)
        if agentid in self.queues_of_agent:
            for queueid in self.queues_of_agent[agentid]:
                self._notify_change(queueid)
        else:
            self.queues_of_agent[agentid] = set()

    def on_agent_loggedoff(self, agentid):
        try:
            self.logged_agents.remove(agentid)
        except KeyError:
            pass
        if agentid in self.queues_of_agent:
            for queueid in self.queues_of_agent[agentid]:
                self._notify_change(queueid)

    def on_agent_removed(self, queueid, agentid):
        self.queues_of_agent[agentid].remove(queueid)
        if agentid in self.logged_agents:
            self._notify_change(queueid)
        logger.info('agent id %s removed from queue id %s', agentid, queueid)

    def on_queue_removed(self, queueid):
        self.queues.remove(queueid)
        for agentid in self.queues_of_agent:
            if queueid in self.queues_of_agent[agentid]:
                self.queues_of_agent[agentid].remove(queueid)

    def on_queue_summary(self, queue_id, counters):
        message = {queue_id: {'Xivo-AvailableAgents': counters.available}}
        self.notifier.on_stat_changed(message)

    def on_agent_called(self, agent_id):
        logger.info('agent id %s called', agent_id)

    def _compute_nb_of_logged_agents(self, queueid):
        nb_of_agent_logged = 0
        for agentid in self.logged_agents:
            if queueid in self.queues_of_agent[agentid]:
                nb_of_agent_logged += 1
        return nb_of_agent_logged

    def _notify_change(self, queueid):
        self.notifier.on_stat_changed({queueid :
                                         { self.LOGGEDAGENT_STATNAME:self._compute_nb_of_logged_agents(queueid)}
                                         })

    def send_all_stats(self, connection_cti):
        logger.info('collect statistics')
        for queueid in self.queues:
            self.notifier.send_statistic({queueid :
                                         { self.LOGGEDAGENT_STATNAME:self._compute_nb_of_logged_agents(queueid)}
                                         }, connection_cti)

    @classmethod
    def get_instance(cls):
        if cls._instance == None:
            cls._instance = cls()
        return cls._instance
