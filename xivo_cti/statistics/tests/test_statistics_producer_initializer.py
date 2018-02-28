# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock, patch
from xivo_cti.services.queue_member.manager import QueueMemberManager
from xivo_cti.statistics.queue_statistics_producer import QueueStatisticsProducer
from xivo_cti.statistics.statistics_producer_initializer import StatisticsProducerInitializer


class TestStatisticsProducerInitializer(unittest.TestCase):

    def setUp(self):
        self.agentd_client = Mock()
        self.queue_member_manager = Mock(QueueMemberManager)
        self.queue_statistics_producer = Mock(QueueStatisticsProducer)
        self.statistics_producer_initializer = StatisticsProducerInitializer(self.queue_member_manager, self.agentd_client)

    @patch('xivo_cti.dao.queue')
    def test_init_queue_statistics_producer_queues(self, mock_queue_dao):
        self.agentd_client.agents.get_agent_statuses.return_value = []
        self.queue_member_manager.get_queue_members.return_value = []
        mock_queue_dao.get_ids.return_value = ['12', '24']

        self.statistics_producer_initializer.init_queue_statistics_producer(self.queue_statistics_producer)

        mock_queue_dao.get_ids.assert_called_once_with()
        self.queue_statistics_producer.on_queue_added.assert_any_call('12')
        self.queue_statistics_producer.on_queue_added.assert_any_call('24')

    @patch('xivo_cti.dao.queue')
    def test_init_queue_statistics_producer_agents(self, mock_queue_dao):
        self.agentd_client.agents.get_agent_statuses.return_value = [
            self._new_agent_status('123', True),
            self._new_agent_status('234', False),
        ]
        self.queue_member_manager.get_queue_members.return_value = []
        mock_queue_dao.get_ids.return_value = []

        self.statistics_producer_initializer.init_queue_statistics_producer(self.queue_statistics_producer)

        self.agentd_client.agents.get_agent_statuses.assert_called_once_with()
        self.queue_statistics_producer.on_agent_loggedon.assert_called_once_with('Agent/123')

    def _new_agent_status(self, agent_number, logged):
        agent_status = Mock()
        agent_status.number = agent_number
        agent_status.logged = logged
        return agent_status
