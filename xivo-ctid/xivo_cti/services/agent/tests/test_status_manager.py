# -*- coding: UTF-8 -*-

# Copyright (C) 2013  Avencall
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

from xivo_cti.services.agent.availability_computer import AgentAvailabilityComputer
from xivo_cti.services.agent.status_manager import AgentStatusManager
from xivo_cti.services.call.direction import CallDirection
from xivo_cti import dao
from xivo_cti.dao.agent_dao import AgentDAO, AgentCallStatus
from xivo_cti.scheduler import Scheduler
from xivo_cti.dao.innerdata_dao import InnerdataDAO

AGENT_ID = 13


class TestAgentStatusManager(unittest.TestCase):

    def setUp(self):
        dao.agent = Mock(AgentDAO)
        self.agent_availability_computer = Mock(AgentAvailabilityComputer)
        dao.innerdata = Mock(InnerdataDAO)
        self.scheduler = Mock(Scheduler)
        self.agent_status_manager = AgentStatusManager(self.agent_availability_computer, self.scheduler)

    def test_agent_logged_in(self):
        self.agent_status_manager.agent_logged_in(AGENT_ID)

        self.agent_availability_computer.compute.assert_called_once_with(AGENT_ID)

    def test_agent_logged_out(self):
        self.agent_status_manager.agent_logged_out(AGENT_ID)

        dao.agent.set_on_wrapup.assert_called_once_with(AGENT_ID, False)
        self.agent_availability_computer.compute.assert_called_once_with(AGENT_ID)

    def test_device_in_use_incoming_external(self):
        given_direction = CallDirection.incoming
        given_is_internal = False
        expected_call_status = AgentCallStatus(direction=given_direction,
                                               is_internal=given_is_internal)

        self.agent_status_manager.device_in_use(AGENT_ID, given_direction, given_is_internal)

        dao.agent.set_nonacd_call_status.assert_called_once_with(AGENT_ID, expected_call_status)
        self.agent_availability_computer.compute.assert_called_once_with(AGENT_ID)

    def test_device_in_use_outgoing_internal(self):
        given_direction = CallDirection.outgoing
        given_is_internal = True
        expected_call_status = AgentCallStatus(direction=given_direction,
                                               is_internal=given_is_internal)

        self.agent_status_manager.device_in_use(AGENT_ID, given_direction, given_is_internal)

        dao.agent.set_nonacd_call_status.assert_called_once_with(AGENT_ID, expected_call_status)
        self.agent_availability_computer.compute.assert_called_once_with(AGENT_ID)

    def test_device_not_in_use(self):
        expected_call_status = None

        self.agent_status_manager.device_not_in_use(AGENT_ID)

        dao.agent.set_nonacd_call_status.assert_called_once_with(AGENT_ID, expected_call_status)
        self.agent_availability_computer.compute.assert_called_once_with(AGENT_ID)

    def test_acd_call_start(self):
        expected_on_call_acd = True

        self.agent_status_manager.acd_call_start(AGENT_ID)

        dao.agent.set_on_call_acd.assert_called_once_with(AGENT_ID, expected_on_call_acd)
        self.agent_availability_computer.compute.assert_called_once_with(AGENT_ID)

    def test_acd_call_end(self):
        expected_on_call_acd = False

        self.agent_status_manager.acd_call_end(AGENT_ID)

        dao.agent.set_on_call_acd.assert_called_once_with(AGENT_ID, expected_on_call_acd)
        self.agent_availability_computer.compute.assert_called_once_with(AGENT_ID)

    def test_agent_in_wrapup(self):
        expected_on_call_acd = False
        expected_in_wrapup = True
        wrapup_time = 10

        self.agent_status_manager.agent_in_wrapup(AGENT_ID, wrapup_time)

        dao.agent.set_on_call_acd.assert_called_once_with(AGENT_ID, expected_on_call_acd)
        dao.agent.set_on_wrapup.assert_called_once_with(AGENT_ID, expected_in_wrapup)
        self.agent_availability_computer.compute.assert_called_once_with(AGENT_ID)
        self.scheduler.schedule.assert_called_once_with(wrapup_time, self.agent_status_manager.agent_wrapup_completed, AGENT_ID)

    def test_agent_wrapup_completed(self):
        expected_in_wrapup = False

        self.agent_status_manager.agent_wrapup_completed(AGENT_ID)

        dao.agent.set_on_wrapup.assert_called_once_with(AGENT_ID, expected_in_wrapup)
        self.agent_availability_computer.compute.assert_called_once_with(AGENT_ID)

    def test_agent_paused_all(self):
        self.agent_status_manager.agent_paused_all(AGENT_ID)

        self.agent_availability_computer.compute.assert_called_once_with(AGENT_ID)

    def test_agent_unpaused(self):
        self.agent_status_manager.agent_unpaused(AGENT_ID)

        self.agent_availability_computer.compute.assert_called_once_with(AGENT_ID)
