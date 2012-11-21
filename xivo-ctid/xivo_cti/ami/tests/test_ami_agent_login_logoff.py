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
from xivo_cti.ami.ami_agent_login_logoff import AMIAgentLoginLogoff
from tests.mock import Mock
from xivo_dao.agentfeaturesdao import AgentFeaturesDAO
from xivo_cti.statistics.queue_statistics_producer import QueueStatisticsProducer
from xivo_cti.dao.innerdatadao import InnerdataDAO
from xivo_cti.services.agent_status import AgentStatus


class TestAMIAgentLoginLogoff(unittest.TestCase):
    def setUp(self):
        self.ami_agent_login_logoff = AMIAgentLoginLogoff()
        self.queue_statistics_producer = Mock(QueueStatisticsProducer)
        self.ami_agent_login_logoff.queue_statistics_producer = self.queue_statistics_producer

    def test_receive_event_agentlogin(self):
        event = {'Agent': '22011'}

        self.ami_agent_login_logoff.on_event_agent_login(event)

        self.queue_statistics_producer.on_agent_loggedon.assert_called_with('Agent/22011')

    def test_receive_event_agentlogoff(self):
        event = {'Agent': '22011'}

        self.ami_agent_login_logoff.on_event_agent_logoff(event)

        self.queue_statistics_producer.on_agent_loggedoff.assert_called_with('Agent/22011')

    def test_on_event_agent_init_received(self):
        event = {'Agent': '22011', 'Status': 'AGENT_IDLE'}
        init_queue_stats_producer = Mock()
        init_agents_status = Mock()
        self.ami_agent_login_logoff._initialize_queue_statistics_producer = init_queue_stats_producer
        self.ami_agent_login_logoff._initialize_agents_status = init_agents_status

        self.ami_agent_login_logoff.on_event_agent_init(event)

        init_queue_stats_producer.assert_called_once_with(event)
        init_agents_status.assert_called_once_with(event)

    def test_initialize_statistics_producer_with_agent_idle(self):
        event = {'Agent': '22011', 'Status': 'AGENT_IDLE'}

        self.ami_agent_login_logoff._initialize_queue_statistics_producer(event)

        self.queue_statistics_producer.on_agent_loggedon.assert_called_with('Agent/22011')

    def test_initialize_statistics_producer_with_agent_talking(self):
        event = {'Agent': '22011', 'Status': 'AGENT_ONCALL'}

        self.ami_agent_login_logoff._initialize_queue_statistics_producer(event)

        self.queue_statistics_producer.on_agent_loggedon.assert_called_with('Agent/22011')

    def test_initialize_statistics_producer_with_agent_other_status(self):
        event = {'Agent': '22011', 'Status': 'AGENT_LOGGEDOFF'}

        self.ami_agent_login_logoff._initialize_queue_statistics_producer(event)

        self.queue_statistics_producer.on_agent_loggedon.assert_never_called()

    def test_initialize_agents_status(self):
        event = {'Agent': '22011', 'Status': 'AGENT_LOGGEDOFF'}
        agent_dao = Mock(AgentFeaturesDAO)
        agent_dao.agent_id.return_value = 1234
        self.ami_agent_login_logoff.agent_features_dao = agent_dao
        innerdata_dao = Mock(InnerdataDAO)
        self.ami_agent_login_logoff.innerdata_dao = innerdata_dao

        self.ami_agent_login_logoff._initialize_agents_status(event)

        agent_dao.agent_id.assert_called_once_with('22011')
        innerdata_dao.set_agent_availability.assert_called_once_with(1234, AgentStatus.logged_out)
