# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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

from functools import partial
from mock import Mock, patch

from xivo_cti import dao
from xivo_cti.dao.agent_dao import AgentDAO
from xivo_cti.services.agent.availability_updater import AgentAvailabilityUpdater
from xivo_cti.services.agent.availability_computer import AgentAvailabilityComputer
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.services.call.direction import CallDirection

AGENT_ID = 13


def when(paused=False, wrapup=False, non_acd=None, on_acd=False, logged_in=True):
    dao.agent.is_completely_paused.return_value = paused
    dao.agent.on_wrapup.return_value = wrapup
    dao.agent.on_call_acd.return_value = on_acd
    dao.agent.nonacd_call_status.return_value = non_acd
    dao.agent.on_call_nonacd.return_value = non_acd is not None

then = None


class TestAgentAvailabilityComputer(unittest.TestCase):

    def setUp(self):
        global then
        self.agent_availability_updater = Mock(AgentAvailabilityUpdater)
        self.availability_computer = AgentAvailabilityComputer(self.agent_availability_updater)
        then = partial(self.agent_availability_updater.update.assert_called_once_with, AGENT_ID)
        dao.agent = Mock(AgentDAO)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_available(self):
        when(logged_in=True)

        self.availability_computer.compute(AGENT_ID)

        then(AgentStatus.available)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_paused(self):
        when(paused=True)

        self.availability_computer.compute(AGENT_ID)

        then(AgentStatus.unavailable)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=False))
    def test_compute_logout(self):
        when(logged_in=False)

        self.availability_computer.compute(AGENT_ID)

        then(AgentStatus.logged_out)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_call_acd(self):
        when(on_acd=True)

        self.availability_computer.compute(AGENT_ID)

        then(AgentStatus.unavailable)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_wrapup(self):
        when(wrapup=True)

        self.availability_computer.compute(AGENT_ID)

        then(AgentStatus.unavailable)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_wrapup_pause(self):
        when(paused=True, wrapup=True)

        self.availability_computer.compute(AGENT_ID)

        then(AgentStatus.unavailable)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_call_acd_pause(self):
        when(paused=True, on_acd=True)

        self.availability_computer.compute(AGENT_ID)

        then(AgentStatus.unavailable)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_call_nonacd_incoming_internal(self):
        call = Mock(direction=CallDirection.incoming, is_internal=True)
        when(non_acd=call)

        self.availability_computer.compute(AGENT_ID)

        then(AgentStatus.on_call_nonacd_incoming_internal)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_call_nonacd_incoming_external(self):
        call = Mock(direction=CallDirection.incoming, is_internal=False)
        when(non_acd=call)

        self.availability_computer.compute(AGENT_ID)

        then(AgentStatus.on_call_nonacd_incoming_external)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_call_nonacd_outgoing_internal(self):
        call = Mock(direction=CallDirection.outgoing, is_internal=True)
        when(non_acd=call)

        self.availability_computer.compute(AGENT_ID)

        then(AgentStatus.on_call_nonacd_outgoing_internal)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_call_nonacd_outgoing_external(self):
        call = Mock(direction=CallDirection.outgoing, is_internal=False)
        when(non_acd=call)

        self.availability_computer.compute(AGENT_ID)

        then(AgentStatus.on_call_nonacd_outgoing_external)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_call_nonacd_wrapup(self):
        call = Mock(direction=CallDirection.outgoing, is_internal=False)
        when(non_acd=call, wrapup=True)

        self.availability_computer.compute(AGENT_ID)

        then(AgentStatus.on_call_nonacd_outgoing_external)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=True))
    def test_compute_call_nonacd_pause(self):
        call = Mock(direction=CallDirection.outgoing, is_internal=False)
        when(non_acd=call, paused=True)

        self.availability_computer.compute(AGENT_ID)

        then(AgentStatus.on_call_nonacd_outgoing_external)

    @patch('xivo_dao.agent_status_dao.is_agent_logged_in', Mock(return_value=False))
    def test_compute_call_nonacd_logout(self):
        call = Mock(direction=CallDirection.outgoing, is_internal=False)
        when(non_acd=call, logged_in=False)

        self.availability_computer.compute(AGENT_ID)

        then(AgentStatus.logged_out)
