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
from tests.mock import Mock
from xivo_cti.scheduler import Scheduler
from xivo_cti.services.agent_status import AgentStatus
from xivo_cti.services.agent_status_notifier import AgentStatusNotifier
from xivo_cti.dao.innerdatadao import InnerdataDAO


class TestAgentStatusNotifier(unittest.TestCase):

    def setUp(self):
        self.mock_innerdata_dao = Mock(InnerdataDAO)

    def test_agent_logged_in(self):
        agent_status_notifier = AgentStatusNotifier(self.mock_innerdata_dao)

        agent_id = 12

        agent_status_notifier.agent_logged_in(agent_id)

        self.mock_innerdata_dao.set_agent_availability.assert_called_once_with(agent_id,
                                                                               AgentStatus.available)

    def test_agent_logged_out(self):
        agent_status_notifier = AgentStatusNotifier(self.mock_innerdata_dao)

        agent_id = 12

        agent_status_notifier.agent_logged_out(agent_id)

        self.mock_innerdata_dao.set_agent_availability.assert_called_once_with(agent_id,
                                                                               AgentStatus.logged_out)

    def test_agent_answered(self):
        agent_status_notifier = AgentStatusNotifier(self.mock_innerdata_dao)

        agent_id = 12

        agent_status_notifier.agent_answered(agent_id)

        self.mock_innerdata_dao.set_agent_availability.assert_called_once_with(agent_id,
                                                                               AgentStatus.unavailable)

    def test_agent_call_completed(self):
        mock_scheduler = Mock(Scheduler)
        agent_status_notifier = AgentStatusNotifier(self.mock_innerdata_dao, mock_scheduler)

        agent_id = 12
        wrapup_time = 25

        agent_status_notifier.agent_call_completed(agent_id, wrapup_time)

        mock_scheduler.schedule.assert_called_once_with(wrapup_time,
                                                        agent_status_notifier.agent_wrapup_completed,
                                                        agent_id)

    def test_agent_call_completed_no_wrapup(self):
        mock_scheduler = Mock(Scheduler)
        agent_status_notifier = AgentStatusNotifier(self.mock_innerdata_dao, mock_scheduler)

        agent_id = 12
        wrapup_time = 0

        agent_status_notifier.agent_call_completed(agent_id, wrapup_time)

        self.assertEqual(mock_scheduler.schedule.call_count, 0)

        self.mock_innerdata_dao.set_agent_availability.assert_called_once_with(agent_id, AgentStatus.available)

    def test_agent_wrapup_completed(self):
        agent_status_notifier = AgentStatusNotifier(self.mock_innerdata_dao)

        agent_id = 12

        agent_status_notifier.agent_wrapup_completed(agent_id)

        self.mock_innerdata_dao.set_agent_availability.assert_called_once_with(agent_id, AgentStatus.available)

    def test_agent_paused_all(self):
        agent_status_notifier = AgentStatusNotifier(self.mock_innerdata_dao)

        agent_id = 12

        agent_status_notifier.agent_paused_all(agent_id)

        self.mock_innerdata_dao.set_agent_availability.assert_called_once_with(agent_id, AgentStatus.unavailable)

    def test_agent_unpaused(self):
        agent_status_notifier = AgentStatusNotifier(self.mock_innerdata_dao)

        agent_id = 12

        agent_status_notifier.agent_unpaused(agent_id)

        self.mock_innerdata_dao.set_agent_availability.assert_called_once_with(agent_id, AgentStatus.available)
