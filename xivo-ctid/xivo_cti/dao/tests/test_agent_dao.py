# -*- coding: utf-8 -*-

# Copyright (C) 2007-2012  Avencall

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
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
from xivo_cti.dao.agent_dao import AgentDAO
from xivo_cti.dao.queue_member_dao import QueueMemberDAO
from xivo_cti import innerdata
from xivo_cti.services.agent_status import AgentStatus


class TestAgentDAO(unittest.TestCase):

    def setUp(self):
        self.innerdata = Mock(innerdata.Safe)

    def test_get_id_from_interface(self):
        agent_number = '1234'
        agent_interface = 'Agent/1234'
        agent_id = 6
        agents_config = Mock()
        agents_config.keeplist = {
            str(agent_id): {
                'number': agent_number,
            }
        }
        self.innerdata.xod_config = {
            'agents': agents_config
        }
        agent_dao = AgentDAO(self.innerdata, Mock())

        result = agent_dao.get_id_from_interface(agent_interface)

        self.assertEqual(result, agent_id)

    def test_get_id_from_number(self):
        agent_number = '1234'
        agent_id = 6
        agents_config = Mock()
        agents_config.keeplist = {
            str(agent_id): {
                'number': agent_number,
            }
        }
        self.innerdata.xod_config = {
            'agents': agents_config
        }
        agent_dao = AgentDAO(self.innerdata, Mock())

        result = agent_dao.get_id_from_number(agent_number)

        self.assertEqual(result, agent_id)

    def test_is_completely_paused_yes(self):
        expected_result = True
        agent_id = 12
        mock_queue_member_dao = Mock(QueueMemberDAO)
        mock_queue_member_dao.get_paused_count_for_agent.return_value = 2
        mock_queue_member_dao.get_queue_count_for_agent.return_value = 2
        agent_dao = AgentDAO(self.innerdata, mock_queue_member_dao)
        agent_dao.get_interface_from_id = Mock(return_value='Agent/1234')

        result = agent_dao.is_completely_paused(agent_id)

        self.assertEqual(result, expected_result)

    def test_is_completely_paused_no(self):
        expected_result = False
        agent_id = 12
        mock_queue_member_dao = Mock(QueueMemberDAO)
        mock_queue_member_dao.get_paused_count_for_agent.return_value = 1
        mock_queue_member_dao.get_queue_count_for_agent.return_value = 2
        agent_dao = AgentDAO(self.innerdata, mock_queue_member_dao)
        agent_dao.get_interface_from_id = Mock(return_value='Agent/1234')

        result = agent_dao.is_completely_paused(agent_id)

        self.assertEqual(result, expected_result)

    def test_is_completely_paused_no_queues(self):
        expected_result = False
        agent_id = 12
        mock_queue_member_dao = Mock(QueueMemberDAO)
        mock_queue_member_dao.get_paused_count_for_agent.return_value = 0
        mock_queue_member_dao.get_queue_count_for_agent.return_value = 0
        agent_dao = AgentDAO(self.innerdata, mock_queue_member_dao)
        agent_dao.get_interface_from_id = Mock(return_value='Agent/1234')

        result = agent_dao.is_completely_paused(agent_id)

        self.assertEqual(result, expected_result)

    def test_get_interface_from_id(self):
        agent_id = 12
        agent_number = '1234'
        expected_interface = 'Agent/1234'

        agent_configs = Mock()
        agent_configs.keeplist = {str(agent_id): {'number': agent_number}}
        self.innerdata.xod_config = {'agents': agent_configs}

        agent_dao = AgentDAO(self.innerdata, Mock())
        result = agent_dao.get_interface_from_id(agent_id)

        self.assertEqual(result, expected_interface)

    def test_is_logged(self):
        agent_id = 12

        agent_status = {str(agent_id): {'availability': AgentStatus.logged_out}}
        self.innerdata.xod_status = {'agents': agent_status}

        agent_dao = AgentDAO(self.innerdata, Mock())

        result = agent_dao.is_logged(agent_id)

        self.assertEqual(result, False)

    def test_is_logged_true(self):
        agent_id = 12

        agent_status = {str(agent_id): {'availability': AgentStatus.available}}
        self.innerdata.xod_status = {'agents': agent_status}

        agent_dao = AgentDAO(self.innerdata, Mock())

        result = agent_dao.is_logged(agent_id)

        self.assertEqual(result, True)
