import logging
from collections import namedtuple
from xivo_cti.ami.ami_callback_handler import AMICallbackHandler
from xivo_cti.services.queue_service_manager import QueueServiceManager
from xivo_cti.services.queue_service_manager import NotAQueueException

logger = logging.getLogger("QueueStatisticsProducer")
QueueCounters = namedtuple('QueueCounters', ['available', 'EWT', 'Talking'])

LOGGEDAGENT_STATNAME = "Xivo-LoggedAgents"
AVAILABLEAGENT_STATNAME = "Xivo-AvailableAgents"
EWT_STATNAME = "Xivo-EWT"
TALKINGAGENT_STATNAME = "Xivo-TalkingAgents"

def register_events():
    callback_handler = AMICallbackHandler.get_instance()
    callback_handler.register_callback('QueueSummary', parse_queue_summary)

def parse_queue_summary(queuesummary_event):
    queue_name = queuesummary_event['Queue']
    counters = QueueCounters(available=queuesummary_event['Available'], EWT=queuesummary_event['HoldTime'], Talking=queuesummary_event['Talking'])

    queue_statistics_producer = QueueStatisticsProducer.get_instance()
    queue_service_manager = QueueServiceManager.get_instance()
    try:
        queue_id = queue_service_manager.get_queue_id(queue_name)
        queue_statistics_producer.on_queue_summary(queue_id, counters)
    except NotAQueueException:
        pass


class QueueStatisticsProducer(object):

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
        self.logged_agents.discard(agentid)
        if agentid in self.queues_of_agent:
            for queueid in self.queues_of_agent[agentid]:
                self._notify_change(queueid)

    def on_agent_removed(self, queueid, agentid):
        self.queues_of_agent[agentid].remove(queueid)
        if agentid in self.logged_agents:
            self._notify_change(queueid)
        logger.debug('agent id %s removed from queue id %s', agentid, queueid)

    def on_queue_removed(self, queueid):
        self.queues.remove(queueid)
        for queues_of_current_agent in self.queues_of_agent.itervalues():
            queues_of_current_agent.discard(queueid)

    def on_queue_summary(self, queue_id, counters):
        message = {queue_id: {AVAILABLEAGENT_STATNAME: counters.available, EWT_STATNAME: counters.EWT, TALKINGAGENT_STATNAME: counters.Talking}}
        self.notifier.on_stat_changed(message)

    def _compute_nb_of_logged_agents(self, queueid):
        nb_of_agent_logged = 0
        for agentid in self.logged_agents:
            if queueid in self.queues_of_agent[agentid]:
                nb_of_agent_logged += 1
        return nb_of_agent_logged

    def _notify_change(self, queueid):
        self.notifier.on_stat_changed({queueid :
                                         { LOGGEDAGENT_STATNAME:self._compute_nb_of_logged_agents(queueid)}
                                         })

    def send_all_stats(self, connection_cti):
        logger.info('collect statistics')
        for queueid in self.queues:
            self.notifier.send_statistic({queueid :
                                         { LOGGEDAGENT_STATNAME:self._compute_nb_of_logged_agents(queueid)}
                                         }, connection_cti)

    @classmethod
    def get_instance(cls):
        if cls._instance == None:
            cls._instance = cls()
        return cls._instance
