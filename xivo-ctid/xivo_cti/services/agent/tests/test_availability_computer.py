# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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
from mock import Mock, patch

from xivo_cti import dao
from xivo_cti.dao.agent_dao import AgentDAO, AgentNonACDStatus
from xivo_cti.services.agent.availability_updater import AgentAvailabilityUpdater
from xivo_cti.services.agent.availability_computer import AgentAvailabilityComputer
from xivo_cti.services.agent.status import AgentStatus

AGENT_ID = 13


class TestAgentAvailabilityComputer(unittest.TestCase):

    def setUp(self):
        self.agent_availability_updater = Mock(AgentAvailabilityUpdater)
        self.availability_computer = AgentAvailabilityComputer(self.agent_availability_updater)
        dao.agent = Mock(AgentDAO)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_available(self):
        dao.agent.on_call_nonacd.return_value = AgentNonACDStatus.no_call
        dao.agent.on_call_acd.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.on_wrapup.return_value = False

        self.availability_computer.compute(AGENT_ID)

        self.agent_availability_updater.update.assert_called_once_with(AGENT_ID, AgentStatus.available)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_paused(self):
        dao.agent.on_call_nonacd.return_value = AgentNonACDStatus.no_call
        dao.agent.on_call_acd.return_value = False
        dao.agent.is_completely_paused.return_value = True
        dao.agent.on_wrapup.return_value = False

        self.availability_computer.compute(AGENT_ID)

        self.agent_availability_updater.update.assert_called_once_with(AGENT_ID, AgentStatus.unavailable)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=False))
    def test_compute_logout(self):
        dao.agent.on_call_nonacd.return_value = AgentNonACDStatus.no_call
        dao.agent.on_call_acd.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.on_wrapup.return_value = False

        self.availability_computer.compute(AGENT_ID)

        self.agent_availability_updater.update.assert_called_once_with(AGENT_ID, AgentStatus.logged_out)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_call_acd(self):
        dao.agent.on_call_nonacd.return_value = AgentNonACDStatus.no_call
        dao.agent.on_call_acd.return_value = True
        dao.agent.is_completely_paused.return_value = False
        dao.agent.on_wrapup.return_value = False

        self.availability_computer.compute(AGENT_ID)

        self.agent_availability_updater.update.assert_called_once_with(AGENT_ID, AgentStatus.unavailable)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_wrapup(self):
        dao.agent.on_call_nonacd.return_value = AgentNonACDStatus.no_call
        dao.agent.on_call_acd.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.on_wrapup.return_value = True

        self.availability_computer.compute(AGENT_ID)

        self.agent_availability_updater.update.assert_called_once_with(AGENT_ID, AgentStatus.unavailable)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_wrapup_pause(self):
        dao.agent.on_call_nonacd.return_value = AgentNonACDStatus.no_call
        dao.agent.on_call_acd.return_value = False
        dao.agent.is_completely_paused.return_value = True
        dao.agent.on_wrapup.return_value = True

        self.availability_computer.compute(AGENT_ID)

        self.agent_availability_updater.update.assert_called_once_with(AGENT_ID, AgentStatus.unavailable)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_call_acd_pause(self):
        dao.agent.on_call_nonacd.return_value = AgentNonACDStatus.no_call
        dao.agent.on_call_acd.return_value = True
        dao.agent.is_completely_paused.return_value = True
        dao.agent.on_wrapup.return_value = False

        self.availability_computer.compute(AGENT_ID)

        self.agent_availability_updater.update.assert_called_once_with(AGENT_ID, AgentStatus.unavailable)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=False))
    def test_compute_logout_call_acd(self):
        dao.agent.on_call_nonacd.return_value = AgentNonACDStatus.no_call
        dao.agent.on_call_acd.return_value = True
        dao.agent.is_completely_paused.return_value = False
        dao.agent.on_wrapup.return_value = False

        self.availability_computer.compute(AGENT_ID)

        self.agent_availability_updater.update.assert_called_once_with(AGENT_ID, AgentStatus.logged_out)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_call_nonacd_incoming(self):
        dao.agent.on_call_nonacd.return_value = AgentNonACDStatus.incoming
        dao.agent.on_call_acd.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.on_wrapup.return_value = False

        self.availability_computer.compute(AGENT_ID)

        self.agent_availability_updater.update.assert_called_once_with(AGENT_ID, AgentStatus.on_call_nonacd_incoming)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_call_nonacd_outgoing(self):
        dao.agent.on_call_nonacd.return_value = AgentNonACDStatus.outgoing
        dao.agent.on_call_acd.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.on_wrapup.return_value = False

        self.availability_computer.compute(AGENT_ID)

        self.agent_availability_updater.update.assert_called_once_with(AGENT_ID, AgentStatus.on_call_nonacd_outgoing)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_call_nonacd_wrapup(self):
        dao.agent.on_call_nonacd.return_value = AgentNonACDStatus.outgoing
        dao.agent.on_call_acd.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.on_wrapup.return_value = True

        self.availability_computer.compute(AGENT_ID)

        self.agent_availability_updater.update.assert_called_once_with(AGENT_ID, AgentStatus.unavailable)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_call_nonacd_pause(self):
        dao.agent.on_call_nonacd.return_value = AgentNonACDStatus.outgoing
        dao.agent.on_call_acd.return_value = False
        dao.agent.is_completely_paused.return_value = True
        dao.agent.on_wrapup.return_value = False

        self.availability_computer.compute(AGENT_ID)

        self.agent_availability_updater.update.assert_called_once_with(AGENT_ID, AgentStatus.unavailable)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=False))
    def test_compute_call_nonacd_logout(self):
        dao.agent.on_call_nonacd.return_value = AgentNonACDStatus.outgoing
        dao.agent.on_call_acd.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.on_wrapup.return_value = False

        self.availability_computer.compute(AGENT_ID)

        self.agent_availability_updater.update.assert_called_once_with(AGENT_ID, AgentStatus.logged_out)
