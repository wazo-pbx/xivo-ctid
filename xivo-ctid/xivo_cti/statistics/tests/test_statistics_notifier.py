'''
Created on 2012-04-25

@author: jylebleu
'''
import unittest
from xivo_cti.statistics.statistics_notifier import StatisticsNotifier
from tests.mock import Mock
from xivo_cti.client_connection import ClientConnection


class TestStatisticsNotifier(unittest.TestCase):

    def setUp(self):
        self.notifier = StatisticsNotifier()


    def tearDown(self):
        pass


    def test_subscribe(self):
        cti_connection = Mock()

        statistic = {'stat':'123'}
        self.notifier.on_stat_changed(statistic)

        self.notifier.subscribe(cti_connection)

        cti_connection.send_message.assert_called_once_with({'class':'getqueuesstats',
                                                              'stats' : statistic
                                                              })

    def test_on_stat_changed_with_one_subscriber(self):
        cti_connection = Mock()
        statistic = {'stat':'123'}

        self.notifier.subscribe(cti_connection)

        self.notifier.on_stat_changed(statistic)

        cti_connection.send_message.assert_called_once_with({'class':'getqueuesstats',
                                                              'stats' : statistic
                                                              })

    def test_on_stat_changed_with_subscribers(self):

        cti_connection1 = Mock()
        cti_connection2 = Mock()
        cti_connection3 = Mock()

        statistic = {'stat':'123'}

        self.notifier.subscribe(cti_connection1)
        self.notifier.subscribe(cti_connection2)
        self.notifier.subscribe(cti_connection3)

        self.notifier.on_stat_changed(statistic)

        cti_connection1.send_message.assert_called_once_with({'class':'getqueuesstats',
                                                              'stats' : statistic
                                                              })
        cti_connection2.send_message.assert_called_once_with({'class':'getqueuesstats',
                                                              'stats' : statistic
                                                              })
        cti_connection3.send_message.assert_called_once_with({'class':'getqueuesstats',
                                                              'stats' : statistic
                                                              })


    def test_do_not_notify_twice_same_connection(self):
        cti_connection = Mock()
        statistic = {'stat':'123'}

        self.notifier.subscribe(cti_connection)
        self.notifier.subscribe(cti_connection)

        self.notifier.on_stat_changed(statistic)

        cti_connection.send_message.assert_called_once_with({'class':'getqueuesstats',
                                                              'stats' : statistic
                                                              })

    def test_remove_connection_when_closed(self):
        cti_connection = Mock()
        statistic = {'stat':'123'}

        self.notifier.subscribe(cti_connection)
        cti_connection.send_message.side_effect = ClientConnection.CloseException(1)

        self.notifier.on_stat_changed(statistic)
        cti_connection.reset_mock()

        self.notifier.on_stat_changed(statistic)
        cti_connection.send_message.assert_never_called()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
