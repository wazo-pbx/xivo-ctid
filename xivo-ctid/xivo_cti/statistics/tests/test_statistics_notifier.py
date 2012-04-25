'''
Created on 2012-04-25

@author: jylebleu
'''
import unittest
from xivo_cti.statistics.statistics_notifier import StatisticsNotifier


class TestStatisticsNotifier(unittest.TestCase):


    def setUp(self):
        self.notifier = StatisticsNotifier()


    def tearDown(self):
        pass


    def test_notify_statistics(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
