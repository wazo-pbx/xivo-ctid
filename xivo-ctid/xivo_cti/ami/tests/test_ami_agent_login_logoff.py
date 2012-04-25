'''
Created on 2012-04-25

@author: jylebleu
'''
import unittest
from xivo_cti.ami.ami_agent_login_logoff import AMIAgentLoginLogoff
from tests.mock import Mock
from xivo_cti.statistics.queuestatisticsproducer import QueueStatisticsProducer


class TestAMIAgentLoginLogoff(unittest.TestCase):


    def setUp(self):
        self.ami_agent_login_logoff = AMIAgentLoginLogoff()
        self.queue_statistics_producer = Mock(QueueStatisticsProducer)
        self.ami_agent_login_logoff.queue_statistics_producer = self.queue_statistics_producer

    def tearDown(self):
        pass


    def test_receive_event_agentlogin(self):
        event = {'Agent': '22011'}

        self.ami_agent_login_logoff.on_event_agent_login(event)

        self.queue_statistics_producer.on_agent_loggedon.assert_called_with('Agent/22011')

    def test_receive_event_agentlogoff(self):
        event = {'Agent': '22011'}

        self.ami_agent_login_logoff.on_event_agent_logoff(event)

        self.queue_statistics_producer.on_agent_loggedoff.assert_called_with('Agent/22011')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
