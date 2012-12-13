# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
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
from mock import Mock
from xivo_cti.statistics.statistics_notifier import StatisticsNotifier
from xivo_cti.client_connection import ClientConnection


class TestStatisticsNotifier(unittest.TestCase):

    def setUp(self):
        self.notifier = StatisticsNotifier()

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

    def test_send_statistic(self):
        cti_connection = Mock()
        statistic = {'stat':'123'}

        self.notifier.send_statistic(statistic, cti_connection)


        cti_connection.send_message.assert_called_once_with({'class':'getqueuesstats',
                                                              'stats' : statistic
                                                              })

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
