# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest
from mock import Mock
from xivo_cti.statistics.statistics_notifier import StatisticsNotifier
from xivo_cti.client_connection import ClientConnection
from xivo_cti.cti.cti_group import CTIGroup, CTIGroupFactory


class TestStatisticsNotifier(unittest.TestCase):

    def setUp(self):
        self.cti_group = Mock(CTIGroup)
        self.cti_group_factory = Mock(CTIGroupFactory)
        self.cti_group_factory.new_cti_group.return_value = self.cti_group
        self.notifier = StatisticsNotifier(self.cti_group_factory)

    def test_subscribe(self):
        cti_connection = Mock()

        self.notifier.subscribe(cti_connection)

        self.cti_group.add.assert_called_once_with(cti_connection)

    def test_on_stat_changed(self):
        statistic = {'stat': '123'}

        self.notifier.on_stat_changed(statistic)

        self.cti_group.send_message.assert_called_once_with({'class': 'getqueuesstats',
                                                             'stats': statistic})

    def test_send_statistic(self):
        cti_connection = Mock()
        statistic = {'stat': '123'}
        expected_result = {
            'class': 'getqueuesstats',
            'stats': statistic
        }

        self.notifier.send_statistic(statistic, cti_connection)

        cti_connection.send_message.assert_called_once_with(expected_result)

    def test_send_statistic_doesnt_raise(self):
        statistic = {'stat': '123'}
        cti_connection = Mock()
        cti_connection.send_message.side_effect = ClientConnection.CloseException()

        self.notifier.send_statistic(statistic, cti_connection)
