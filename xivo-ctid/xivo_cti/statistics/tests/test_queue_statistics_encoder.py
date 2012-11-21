# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
