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
from mock import Mock
from xivo_cti import dao
from xivo_cti.dao.agent_dao import AgentDAO
from xivo_cti.services import agent_on_call_updater
from xivo_cti.services.agent_on_call_updater import AgentOnCallUpdater


class TestAgentOnCallUpdater(unittest.TestCase):

    def test_parse_ami_answered(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1234',
                     'Event': 'AgentConnect'}
        dao.agent.get_id_from_interface.return_value = agent_id
        mock_agent_on_call_updater = Mock(AgentOnCallUpdater)

        agent_on_call_updater.parse_ami_answered(ami_event, mock_agent_on_call_updater)

        mock_agent_on_call_updater.answered_call.assert_called_with(agent_id)

    def test_parse_ami_call_completed(self):
        agent_id = 12
        wrapup_time = 15

        ami_event = {'MemberName': 'Agent/1234',
                     'Event': 'AgentComplete',
                     'WrapupTime': str(wrapup_time)}
        dao.agent.get_id_from_interface.return_value = agent_id
        mock_agent_on_call_updater = Mock(AgentOnCallUpdater)

        agent_on_call_updater.parse_ami_call_completed(ami_event, mock_agent_on_call_updater)

        mock_agent_on_call_updater.call_completed.assert_called_with(agent_id)

    def test_answered_call(self):
        agent_id = 12
        dao.agent = Mock(AgentDAO)
        agent_on_call_updater = AgentOnCallUpdater()

        agent_on_call_updater.answered_call(agent_id)

        dao.agent.set_on_call.assert_called_once_with(agent_id, True)

    def test_call_completed(self):
        agent_id = 12
        dao.agent = Mock(AgentDAO)
        agent_on_call_updater = AgentOnCallUpdater()

        agent_on_call_updater.call_completed(agent_id)

        dao.agent.set_on_call.assert_called_once_with(agent_id, False)
