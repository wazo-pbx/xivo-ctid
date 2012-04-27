
import unittest
from xivo_cti.statistics.queuestatisticsproducer import QueueStatisticsProducer
from tests.mock import Mock
from xivo_cti.statistics.statisticsnotifier import StatisticsNotifier


def _aQueueStat():
    return QueueStatBuilder()

class QueueStatBuilder(object):
    def __init__(self):
        self._queueid = ''
        self._loggged_agent = 0

    def in_queue(self, queueid):
        self._queueid = queueid
        return self

    def nb_of_logged_agents(self, logged_agent):
        self._loggged_agent = logged_agent
        return self


    def build(self):
        return {'stats':{self._queueid:{'loggedagents':self._loggged_agent}}}

class Test(unittest.TestCase):


    def setUp(self):
        self.queue_statistics_producer = QueueStatisticsProducer()
        self.statistics_notifier = Mock(StatisticsNotifier)
        self.queue_statistics_producer.set_notifier(self.statistics_notifier)


    def tearDown(self):
        pass


    def test_log_one_agent(self):

        queueid = 32
        agentid = 42
        self.queue_statistics_producer.on_queue_added(queueid)
        self.queue_statistics_producer.on_agent_added(queueid, agentid)


        self.queue_statistics_producer.on_agent_loggedon(agentid)

        self.statistics_notifier.on_stat_changed.assert_called_once_with(_aQueueStat()
                                                                            .in_queue(queueid)
                                                                            .nb_of_logged_agents(1)
                                                                            .build())

    def test_log_agents(self):

        queueid = 32
        agentid1 = 42
        agentid2 = 27
        self.queue_statistics_producer.on_queue_added(queueid)
        self.queue_statistics_producer.on_agent_added(queueid, agentid1)
        self.queue_statistics_producer.on_agent_added(queueid, agentid2)


        self.queue_statistics_producer.on_agent_loggedon(agentid1)
        self.statistics_notifier.on_stat_changed.assert_called_with(_aQueueStat()
                                                                            .in_queue(queueid)
                                                                            .nb_of_logged_agents(1)
                                                                            .build())

        self.queue_statistics_producer.on_agent_loggedon(agentid2)
        self.statistics_notifier.on_stat_changed.assert_called_with(_aQueueStat()
                                                                            .in_queue(queueid)
                                                                            .nb_of_logged_agents(2)
                                                                            .build())

    def test_log_agent_with_multiple_queues(self):
        queue1_id = 32
        queue2_id = 36
        agentid1 = 42
        self.queue_statistics_producer.on_queue_added(queue1_id)
        self.queue_statistics_producer.on_queue_added(queue2_id)
        self.queue_statistics_producer.on_agent_added(queue1_id, agentid1)

        self.queue_statistics_producer.on_agent_loggedon(agentid1)
        self.statistics_notifier.on_stat_changed.assert_called_with(_aQueueStat()
                                                                            .in_queue(queue1_id)
                                                                            .nb_of_logged_agents(1)
                                                                            .build())

    def test_log_agent_on_multiple_queues(self):
        queue1_id = 32
        queue2_id = 36
        agentid1 = 42
        self.queue_statistics_producer.on_queue_added(queue1_id)
        self.queue_statistics_producer.on_queue_added(queue2_id)
        self.queue_statistics_producer.on_agent_added(queue1_id, agentid1)
        self.queue_statistics_producer.on_agent_added(queue2_id, agentid1)

        self.queue_statistics_producer.on_agent_loggedon(agentid1)
        self.statistics_notifier.on_stat_changed.assert_was_called_with(_aQueueStat()
                                                                            .in_queue(queue1_id)
                                                                            .nb_of_logged_agents(1)
                                                                            .build())
        self.statistics_notifier.on_stat_changed.assert_was_called_with(_aQueueStat()
                                                                            .in_queue(queue2_id)
                                                                            .nb_of_logged_agents(1)
                                                                            .build())

    def _add_agent(self, queueid, agentid):
        self.queue_statistics_producer.on_queue_added(queueid)
        self.queue_statistics_producer.on_agent_added(queueid, agentid)

    def _log_agent(self, agentid):
        self.queue_statistics_producer.on_agent_loggedon(agentid)
        self.statistics_notifier.reset_mock()

    def test_logoff_agent(self):
        queueid = 987
        agentid = 1256

        self._add_agent(queueid, agentid)
        self._log_agent(agentid)

        self.queue_statistics_producer.on_agent_loggedoff(agentid)

        self.statistics_notifier.on_stat_changed.assert_called_with(_aQueueStat()
                                                                            .in_queue(queueid)
                                                                            .nb_of_logged_agents(0)
                                                                            .build())

    def test_remove_logged_agent_on_one_queue(self):
        queueid = 987
        agentid = 1256

        self._add_agent(queueid, agentid)
        self._log_agent(agentid)

        self.queue_statistics_producer.on_agent_removed(queueid, agentid)

        self.statistics_notifier.on_stat_changed.assert_called_once_with(_aQueueStat()
                                                                            .in_queue(queueid)
                                                                            .nb_of_logged_agents(0)
                                                                            .build())

    def test_remove_logged_agent_on_multiple_queues(self):
        queue1_id = 987
        queue2_id = 1024
        agentid = 1256

        self._add_agent(queue1_id, agentid)
        self._add_agent(queue2_id, agentid)
        self._log_agent(agentid)

        self.queue_statistics_producer.on_agent_removed(queue1_id, agentid)

        self.statistics_notifier.on_stat_changed.assert_called_once_with(_aQueueStat()
                                                                            .in_queue(queue1_id)
                                                                            .nb_of_logged_agents(0)
                                                                            .build())

    def test_remove_unlogged_agent_from_one_queue(self):
        queue1_id = 987
        agentid = 1256

        self._add_agent(queue1_id, agentid)

        self.queue_statistics_producer.on_agent_removed(queue1_id, agentid)

        self.statistics_notifier.on_stat_changed.assert_never_called()

    def test_remove_unlogged_agent_from_one_queue_multiple_queues(self):

        queue1_id = 987
        queue2_id = 1024
        agentid = 1256

        self._add_agent(queue1_id, agentid)
        self._add_agent(queue2_id, agentid)

        self.queue_statistics_producer.on_agent_removed(queue1_id, agentid)

        self.queue_statistics_producer.on_agent_loggedon(agentid)

        self.statistics_notifier.on_stat_changed.assert_called_once_with(_aQueueStat()
                                                                            .in_queue(queue2_id)
                                                                            .nb_of_logged_agents(1)
                                                                            .build())

    def test_remove_queue(self):

        queue1_id = 987
        queue2_id = 1024
        agentid = 1256

        self._add_agent(queue1_id, agentid)
        self._add_agent(queue2_id, agentid)

        self.queue_statistics_producer.on_queue_removed(queue1_id)

        self.queue_statistics_producer.on_agent_loggedon(agentid)

        self.statistics_notifier.on_stat_changed.assert_called_once_with(_aQueueStat()
                                                                            .in_queue(queue2_id)
                                                                            .nb_of_logged_agents(1)
                                                                            .build())

    def test_remove_queue_with_no_agents(self):
        queue_to_remove = 777
        otheragent = 345
        otherqueue = 962
        self._add_agent(otherqueue, otheragent)

        self.queue_statistics_producer.on_queue_added(queue_to_remove)
        self.queue_statistics_producer.on_queue_removed(queue_to_remove)

        self.assertTrue(True, 'should not raise any error')

    def test_logon_agent_with_no_queues(self):
        agentid = 1256

        self.queue_statistics_producer.on_agent_loggedon(agentid)

        self.assertTrue(True, 'should not raise any error')

    def test_logoff_agent_with_no_queues(self):
        agentid = 1256

        self.queue_statistics_producer.on_agent_loggedoff(agentid)

        self.assertTrue(True, 'should not raise any error')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testAgentLogon']
    unittest.main()
