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

from xivo_cti.services.agent.availability_updater import AgentAvailabilityUpdater
from xivo_cti.services.agent.status_manager import AgentStatusManager
from xivo_cti import dao
from xivo_cti.dao.agent_dao import AgentDAO
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.scheduler import Scheduler
from xivo_cti.dao.innerdata_dao import InnerdataDAO


class TestAgentStatusManager(unittest.TestCase):

    def setUp(self):
        dao.agent = Mock(AgentDAO)
        self.agent_availability_updater = Mock(AgentAvailabilityUpdater)
        dao.innerdata = Mock(InnerdataDAO)
        self.agent_status_manager = AgentStatusManager(self.agent_availability_updater, Mock(Scheduler))

    def test_agent_logged_in(self):
        dao.agent.is_completely_paused.return_value = False
        dao.agent.on_call_nonacd.return_value = False

        agent_id = 12

        self.agent_status_manager.agent_logged_in(agent_id)

        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.available)

    def test_agent_logged_in_paused(self):
        dao.agent.is_completely_paused.return_value = True
        dao.agent.on_call_nonacd.return_value = False

        agent_id = 12

        self.agent_status_manager.agent_logged_in(agent_id)

        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.unavailable)

    def test_agent_logged_in_call(self):
        dao.agent.is_completely_paused.return_value = False
        dao.agent.on_call_nonacd.return_value = True

        agent_id = 12

        self.agent_status_manager.agent_logged_in(agent_id)

        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.on_call_nonacd)

    def test_agent_logged_out(self):
        agent_id = 12

        self.agent_status_manager.agent_logged_out(agent_id)

        dao.agent.set_on_wrapup.assert_called_once_with(agent_id, False)
        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.logged_out)

    def test_device_in_use_when_available(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_nonacd.return_value = False
        dao.agent.on_call_acd.return_value = False

        self.agent_status_manager.device_in_use(agent_id)

        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.on_call_nonacd)
        dao.agent.set_on_call_nonacd.assert_called_once_with(agent_id, True)

    def test_device_in_use_when_wrapup(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = True
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_nonacd.return_value = False
        dao.agent.on_call_acd.return_value = False

        self.agent_status_manager.device_in_use(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)
        dao.agent.set_on_call_nonacd.assert_called_once_with(agent_id, True)

    def test_device_in_use_when_paused(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = False
        dao.agent.is_completely_paused.return_value = True
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_nonacd.return_value = False
        dao.agent.on_call_acd.return_value = False

        self.agent_status_manager.device_in_use(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)
        dao.agent.set_on_call_nonacd.assert_called_once_with(agent_id, True)

    def test_device_in_use_when_unlogged(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = False
        dao.agent.on_call_nonacd.return_value = False
        dao.agent.on_call_acd.return_value = False

        self.agent_status_manager.device_in_use(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)
        dao.agent.set_on_call_nonacd.assert_called_once_with(agent_id, True)

    def test_device_in_use_when_on_call_nonacd(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_nonacd.return_value = True
        dao.agent.on_call_acd.return_value = False

        self.agent_status_manager.device_in_use(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)
        self.assertEquals(dao.agent.set_on_call_nonacd.call_count, 0)

    def test_device_in_use_when_on_call_acd(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_nonacd.return_value = False
        dao.agent.on_call_acd.return_value = True

        self.agent_status_manager.device_in_use(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)
        dao.agent.set_on_call_nonacd.assert_called_once_with(agent_id, True)

    def test_device_not_in_use_when_on_call_nonacd(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_acd.return_value = False
        dao.agent.on_call_nonacd.return_value = True

        self.agent_status_manager.device_not_in_use(agent_id)

        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.available)
        dao.agent.set_on_call_nonacd.assert_called_once_with(agent_id, False)

    def test_device_not_in_use_when_on_call_acd(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_acd.return_value = True
        dao.agent.on_call_nonacd.return_value = True

        self.agent_status_manager.device_not_in_use(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)
        dao.agent.set_on_call_nonacd.assert_called_once_with(agent_id, False)

    def test_device_not_in_use_when_available(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_acd.return_value = False
        dao.agent.on_call_nonacd.return_value = False

        self.agent_status_manager.device_not_in_use(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)
        self.assertEquals(dao.agent.set_on_call_nonacd.call_count, 0)

    def test_device_not_in_use_when_wrapup(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = True
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_acd.return_value = False
        dao.agent.on_call_nonacd.return_value = True

        self.agent_status_manager.device_not_in_use(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)
        dao.agent.set_on_call_nonacd.assert_called_once_with(agent_id, False)

    def test_device_not_in_use_when_paused(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = False
        dao.agent.is_completely_paused.return_value = True
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_acd.return_value = False
        dao.agent.on_call_nonacd.return_value = True

        self.agent_status_manager.device_not_in_use(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)
        dao.agent.set_on_call_nonacd.assert_called_once_with(agent_id, False)

    def test_device_not_in_use_when_unlogged(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = False
        dao.agent.on_call_acd.return_value = False
        dao.agent.on_call_nonacd.return_value = True

        self.agent_status_manager.device_not_in_use(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)
        dao.agent.set_on_call_nonacd.assert_called_once_with(agent_id, False)

    def test_acd_call_start_when_available(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_acd.return_value = False
        dao.agent.on_call_nonacd.return_value = False

        self.agent_status_manager.acd_call_start(agent_id)

        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.unavailable)
        dao.agent.set_on_call_acd.assert_called_once_with(agent_id, True)

    def test_acd_call_end_when_on_call_acd(self):
        agent_id = 12
        dao.agent.is_completely_paused.return_value = False
        dao.agent.on_call_acd.return_value = True

        self.agent_status_manager.acd_call_end(agent_id)

        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.available)
        dao.agent.set_on_call_acd.assert_called_once_with(agent_id, False)

    def test_acd_call_end_when_on_call_acd_and_paused(self):
        agent_id = 12
        dao.agent.is_completely_paused.return_value = True
        dao.agent.on_call_acd.return_value = True

        self.agent_status_manager.acd_call_end(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)
        dao.agent.set_on_call_acd.assert_called_once_with(agent_id, False)

    def test_agent_in_wrapup(self):
        agent_id = 12
        wrapup_time = 25

        self.agent_status_manager.agent_in_wrapup(agent_id, wrapup_time)

        dao.agent.set_on_wrapup.assert_called_once_with(agent_id, True)
        dao.agent.set_on_call_acd.assert_called_once_with(agent_id, False)
        self.agent_status_manager.scheduler.schedule.assert_called_once_with(
            wrapup_time,
            self.agent_status_manager.agent_wrapup_completed,
            agent_id
        )
        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_agent_wrapup_completed(self):
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_nonacd.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_wrapup_completed(agent_id)

        dao.agent.set_on_wrapup.assert_called_once_with(agent_id, False)
        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.available)

    def test_agent_wrapup_completed_in_pause(self):
        dao.agent.is_completely_paused.return_value = True
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_nonacd.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_wrapup_completed(agent_id)

        dao.agent.set_on_wrapup.assert_called_once_with(agent_id, False)
        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_agent_wrapup_completed_logged_out(self):
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = False
        dao.agent.on_call_nonacd.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_wrapup_completed(agent_id)

        dao.agent.set_on_wrapup.assert_called_once_with(agent_id, False)
        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_agent_wrapup_completed_on_call_nonacd(self):
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_nonacd.return_value = True
        agent_id = 12

        self.agent_status_manager.agent_wrapup_completed(agent_id)

        dao.agent.set_on_wrapup.assert_called_once_with(agent_id, False)
        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.on_call_nonacd)

    def test_agent_paused_all(self):
        dao.agent.is_logged.return_value = True
        agent_id = 12

        self.agent_status_manager.agent_paused_all(agent_id)

        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.unavailable)

    def test_agent_paused_all_while_unlogged(self):
        dao.agent.is_logged.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_paused_all(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_agent_unpaused(self):
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_nonacd.return_value = False
        dao.agent.on_call_acd.return_value = False
        dao.agent.on_wrapup.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_unpaused(agent_id)

        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.available)

    def test_agent_unpaused_on_call_nonacd(self):
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_nonacd.return_value = True
        dao.agent.on_call_acd.return_value = False
        dao.agent.on_wrapup.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_unpaused(agent_id)

        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.on_call_nonacd)

    def test_agent_unpaused_on_call_acd(self):
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_nonacd.return_value = False
        dao.agent.on_call_acd.return_value = True
        dao.agent.on_wrapup.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_unpaused(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_agent_unpaused_while_unlogged(self):
        dao.agent.is_logged.return_value = False
        dao.agent.on_call_nonacd.return_value = False
        dao.agent.on_call_acd.return_value = False
        dao.agent.on_wrapup.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_unpaused(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_agent_unpaused_on_wrapup(self):
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_nonacd.return_value = False
        dao.agent.on_call_acd.return_value = False
        dao.agent.on_wrapup.return_value = True
        agent_id = 12

        self.agent_status_manager.agent_unpaused(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)
