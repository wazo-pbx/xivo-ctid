# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.model.queuestatistic import QueueStatistic
from xivo_cti.statistics.queue_statistics_encoder import QueueStatisticsEncoder


class TestQueueStatisticsEncoder(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 1000

    def tearDown(self):
        pass

    def test_encode(self):
        '''
         13:54:50.718095 Client > Server
           {"class": "getqueuesstats", "on": {"2": {"window": "3600", "xqos": "60"}, "3": {"window": "3600", "xqos": "60"}}}
        13:54:50.752110 Server > Client
        {"class": "queuestats", "direction": "client", "function": "update", "stats": {"2": {"Xivo-Holdtime-avg": "na", "Xivo-Holdtime-max": "na", "Xivo-Join": "0", "Xivo-Link": "0", "Xivo-Lost": "0", "Xivo-Qos": "na", "Xivo-Rate": "na", "Xivo-TalkingTime": "na"}, "3": {"Xivo-Holdtime-avg": "na", "Xivo-Holdtime-max": "na", "Xivo-Join": "0", "Xivo-Link": "0", "Xivo-Lost": "0", "Xivo-Qos": "na", "Xivo-Rate": "na", "Xivo-TalkingTime": "na"}}, "timenow": 1318960490.74}
        '''
        queuestatistic = QueueStatistic()
        queuestatistic.received_call_count = 5
        queuestatistic.answered_call_count = 7
        queuestatistic.abandonned_call_count = 11
        queuestatistic.efficiency = 33
        queuestatistic.qos = 66
        queuestatistic.max_hold_time = 345
        queuestatistic.mean_hold_time = 33

        expected = {'stats': {'3': {'Xivo-Join': '5',
                                    'Xivo-Link': '7',
                                    'Xivo-Lost': '11',
                                    'Xivo-Rate': '33',
                                    'Xivo-Qos': '66',
                                    'Xivo-Holdtime-avg': '33',
                                    'Xivo-Holdtime-max': '345'}}}

        queuestatisticsencoder = QueueStatisticsEncoder()

        statistic_results = {}
        statistic_results['3'] = queuestatistic

        result = queuestatisticsencoder.encode(statistic_results)

        self.assertEqual(result, expected)
