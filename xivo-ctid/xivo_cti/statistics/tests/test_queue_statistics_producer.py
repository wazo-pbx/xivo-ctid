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
from mock import Mock, patch
from xivo_cti.dao.innerdata_dao import InnerdataDAO
from xivo_cti.statistics import queue_statistics_producer
from xivo_cti.statistics.queue_statistics_producer import QueueStatisticsProducer
from xivo_cti.statistics.queue_statistics_producer import QueueCounters
from xivo_cti.statistics.statistics_notifier import StatisticsNotifier
from xivo_cti.services.queue_service_manager import QueueServiceManager


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
        return {self._queueid: {'Xivo-LoggedAgents': self._loggged_agent}}


class TestQueueStatisticsProducer(unittest.TestCase):

    def setUp(self):
        self.queue_statistics_producer = QueueStatisticsProducer(Mock(StatisticsNotifier))
        self.queue_statistics_producer.dao.innerdata = Mock(InnerdataDAO)
        self.queue_service_manager = Mock(QueueServiceManager)
        self.dependencies = {
            'queue_service_manager': self.queue_service_manager,
            'queue_statistics_producer': self.queue_statistics_producer,
        }
        self.mock_context = lambda module: self.dependencies[module]

    def tearDown(self):
        QueueStatisticsProducer._instance = None

    def test_log_one_agent(self):

        queueid = 32
        agentid = 42
        self._add_queue(queueid)
        self._add_agent(queueid, agentid)

        self.queue_statistics_producer.on_agent_loggedon(agentid)

        self.queue_statistics_producer.notifier.on_stat_changed.assert_called_once_with(_aQueueStat()
                                                                         .in_queue(queueid)
                                                                         .nb_of_logged_agents(1)
                                                                         .build())

    def test_log_agents(self):

        queueid = 32
        agentid1 = 42
        agentid2 = 27
        self._add_queue(queueid)
        self._add_agent(queueid, agentid1)
        self._add_agent(queueid, agentid2)

        self.queue_statistics_producer.on_agent_loggedon(agentid1)

        self.queue_statistics_producer.notifier.on_stat_changed.assert_called_with(_aQueueStat()
                                                                    .in_queue(queueid)
                                                                    .nb_of_logged_agents(1)
                                                                    .build())

        self.queue_statistics_producer.on_agent_loggedon(agentid2)
        self.queue_statistics_producer.notifier.on_stat_changed.assert_called_with(_aQueueStat()
                                                                    .in_queue(queueid)
                                                                    .nb_of_logged_agents(2)
                                                                    .build())

    def test_log_agent_with_multiple_queues(self):
        queue1_id = 32
        queue2_id = 36
        agentid1 = 42
        self._add_queue(queue1_id)
        self._add_queue(queue2_id)
        self._add_agent(queue1_id, agentid1)

        self.queue_statistics_producer.on_agent_loggedon(agentid1)

        self.queue_statistics_producer.notifier.on_stat_changed.assert_called_with(_aQueueStat()
                                                                    .in_queue(queue1_id)
                                                                    .nb_of_logged_agents(1)
                                                                    .build())

    def test_log_agent_on_multiple_queues(self):
        queue1_id = 32
        queue2_id = 36
        agentid1 = 42
        self._add_queue(queue1_id)
        self._add_queue(queue2_id)
        self._add_agent(queue1_id, agentid1)
        self._add_agent(queue2_id, agentid1)

        self.queue_statistics_producer.on_agent_loggedon(agentid1)

        self.queue_statistics_producer.notifier.on_stat_changed.assert_was_called_with(_aQueueStat()
                                                                        .in_queue(queue1_id)
                                                                        .nb_of_logged_agents(1)
                                                                        .build())
        self.queue_statistics_producer.notifier.on_stat_changed.assert_was_called_with(_aQueueStat()
                                                                        .in_queue(queue2_id)
                                                                        .nb_of_logged_agents(1)
                                                                        .build())

    def test_logoff_agent(self):
        queueid = 987
        agentid = 1256

        self._add_agent(queueid, agentid)
        self._log_agent(agentid)

        self.queue_statistics_producer.on_agent_loggedoff(agentid)

        self.queue_statistics_producer.notifier.on_stat_changed.assert_called_with(_aQueueStat()
                                                                    .in_queue(queueid)
                                                                    .nb_of_logged_agents(0)
                                                                    .build())

    def test_remove_logged_agent_on_one_queue(self):
        queueid = 987
        agentid = 1256

        self._add_agent(queueid, agentid)
        self._log_agent(agentid)

        self.queue_statistics_producer._on_agent_removed(queueid, agentid)

        self.queue_statistics_producer.notifier.on_stat_changed.assert_called_once_with(_aQueueStat()
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

        self.queue_statistics_producer._on_agent_removed(queue1_id, agentid)

        self.queue_statistics_producer.notifier.on_stat_changed.assert_called_once_with(_aQueueStat()
                                                                         .in_queue(queue1_id)
                                                                         .nb_of_logged_agents(0)
                                                                         .build())

    def test_remove_unlogged_agent_from_one_queue(self):
        queue1_id = 987
        agentid = 1256

        self._add_agent(queue1_id, agentid)

        self.queue_statistics_producer._on_agent_removed(queue1_id, agentid)

        self.queue_statistics_producer.notifier.on_stat_changed.assert_never_called()

    def test_remove_unlogged_agent_from_one_queue_multiple_queues(self):

        queue1_id = 987
        queue2_id = 1024
        agentid = 1256

        self._add_agent(queue1_id, agentid)
        self._add_agent(queue2_id, agentid)

        self.queue_statistics_producer._on_agent_removed(queue1_id, agentid)

        self.queue_statistics_producer.on_agent_loggedon(agentid)

        self.queue_statistics_producer.notifier.on_stat_changed.assert_called_once_with(_aQueueStat()
                                                                         .in_queue(queue2_id)
                                                                         .nb_of_logged_agents(1)
                                                                         .build())

    def test_add_queue(self):
        queue_id = 27

        self.queue_statistics_producer.on_queue_added(queue_id)

        self.queue_statistics_producer.notifier.on_stat_changed.assert_called_once_with(_aQueueStat()
                                                                         .in_queue(queue_id)
                                                                         .nb_of_logged_agents(0)
                                                                         .build())

    def test_remove_queue(self):

        queue1_id = 987
        queue2_id = 1024
        agentid = 1256

        self._add_agent(queue1_id, agentid)
        self._add_agent(queue2_id, agentid)

        self.queue_statistics_producer.on_queue_removed(queue1_id)

        self.queue_statistics_producer.on_agent_loggedon(agentid)

        self.queue_statistics_producer.notifier.on_stat_changed.assert_called_once_with(_aQueueStat()
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

    def test_add_agent_logged_off(self):
        queueid = 987
        agentid = 1256

        self.queue_statistics_producer._on_agent_added(queueid, agentid)

        self.queue_statistics_producer.notifier.on_stat_changed.assert_called_once_with(_aQueueStat()
                                                                         .in_queue(queueid)
                                                                         .nb_of_logged_agents(0)
                                                                         .build())

    def test_agent_logged_on_added_to_another_queue(self):
        queueid = 88
        other_queue = 90
        agentid = 12

        self._add_queue(other_queue)
        self._add_agent(queueid, agentid)
        self._log_agent(agentid)

        self.queue_statistics_producer._on_agent_added(other_queue, agentid)

        self.queue_statistics_producer.notifier.on_stat_changed.assert_called_once_with(_aQueueStat()
                                                                         .in_queue(other_queue)
                                                                         .nb_of_logged_agents(1)
                                                                         .build())

    def test_send_all_stats(self):
        connection_cti = Mock()
        queueid1 = 1
        queueid2 = 7

        self._add_queue(queueid1)
        self._add_queue(34)
        self._add_queue(queueid2)
        self._remove_queue(34)

        self.queue_statistics_producer.send_all_stats(connection_cti)

        self.queue_statistics_producer.notifier.send_statistic.assert_was_called_with(_aQueueStat()
                                                                       .in_queue(queueid1)
                                                                       .nb_of_logged_agents(0)
                                                                       .build(), connection_cti)

        self.queue_statistics_producer.notifier.send_statistic.assert_was_called_with(_aQueueStat()
                                                                       .in_queue(queueid2)
                                                                       .nb_of_logged_agents(0)
                                                                       .build(), connection_cti)

    def test_send_all_stats_with_agent_in_no_queue(self):
        connection_cti = Mock()
        agent_id = 'Agent/3214'
        queue_id = '53'

        self._log_agent(agent_id)
        self._add_queue(queue_id)

        self.queue_statistics_producer.send_all_stats(connection_cti)

        self.queue_statistics_producer.notifier.send_statistic.assert_called_once_with(_aQueueStat()
                                                                        .in_queue(queue_id)
                                                                        .nb_of_logged_agents(0)
                                                                        .build(), connection_cti)

    @patch('xivo_cti.context.context.get')
    def test_parse_queue_summary(self, mock_context):
        self.queue_statistics_producer.on_queue_summary = Mock()
        queue_name = 'services'
        queue_id = 12
        queuesummary_event = {'Event': 'QueueSummary',
                              'Queue': queue_name,
                              'Available': '5',
                              'Talking': '1',
                              'HoldTime': '7'}
        expected_counters = QueueCounters(available='5', EWT='7', Talking='1')
        mock_context.side_effect = self.mock_context
        self.queue_service_manager.get_queue_id.return_value = queue_id

        queue_statistics_producer.parse_queue_summary(queuesummary_event)

        self.queue_statistics_producer.on_queue_summary.assert_called_once_with(queue_id, expected_counters)

    @patch('xivo_cti.context.context.get')
    def test_parse_queue_summary_not_a_queue(self, mock_context):
        self.queue_statistics_producer.on_queue_summary = Mock()

        queue_name = 'services'
        queuesummary_event = {'Event': 'QueueSummary',
                              'Queue': queue_name,
                              'Available': '5',
                              'Talking': '1',
                              'HoldTime': '7'}
        mock_context.side_effect = self.mock_context

        queue_statistics_producer.parse_queue_summary(queuesummary_event)

        self.queue_statistics_producer.on_queue_summary.assert_never_called()

    def test_on_queue_summary(self):
        queue_name = 'services'
        event_content = QueueCounters(available='3', EWT='55', Talking='1')

        self.queue_statistics_producer.on_queue_summary(queue_name, event_content)

        self.queue_statistics_producer.notifier.on_stat_changed.assert_called_once_with({
            queue_name: {'Xivo-AvailableAgents': event_content.available, 'Xivo-EWT': event_content.EWT, 'Xivo-TalkingAgents': event_content.Talking}
        })

    def _log_agent(self, agentid):
        self.queue_statistics_producer.on_agent_loggedon(agentid)
        self.queue_statistics_producer.notifier.reset_mock()

    def _unlog_agent(self, agentid):
        self.queue_statistics_producer.on_agent_loggedoff(agentid)
        self.queue_statistics_producer.notifier.reset_mock()

    def _add_queue(self, queueid):
        self.queue_statistics_producer.on_queue_added(queueid)
        self.queue_statistics_producer.notifier.reset_mock()

    def _remove_queue(self, queueid):
        self.queue_statistics_producer.on_queue_removed(queueid)
        self.queue_statistics_producer.notifier.reset_mock()

    def _add_agent(self, queueid, agentid):
        self.queue_statistics_producer.on_queue_added(queueid)
        self.queue_statistics_producer._on_agent_added(queueid, agentid)
        self.queue_statistics_producer.notifier.reset_mock()
