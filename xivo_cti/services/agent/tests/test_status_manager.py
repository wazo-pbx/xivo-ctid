# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock
from hamcrest import assert_that, equal_to

from xivo_cti.services.agent.availability_computer import AgentAvailabilityComputer
from xivo_cti.services.agent.status_manager import AgentStatusManager
from xivo_cti.services.call.direction import CallDirection
from xivo_cti import dao
from xivo_cti.dao.agent_dao import AgentDAO, AgentCallStatus
from xivo_cti import task_scheduler
from xivo_cti.dao.innerdata_dao import InnerdataDAO

AGENT_ID = 13


class TestAgentStatusManagerWrapupHandling(unittest.TestCase):

    def setUp(self):
        dao.agent = Mock(AgentDAO)
        self.agent_availability_computer = Mock(AgentAvailabilityComputer)
        dao.innerdata = Mock(InnerdataDAO)
        self.task_scheduler = task_scheduler.new_task_scheduler()
        self.agent_status_manager = AgentStatusManager(self.agent_availability_computer, self.task_scheduler)

    def test_agent_in_wrapup(self):
        expected_on_call_acd = False
        expected_in_wrapup = True
        wrapup_time = 10

        self.agent_status_manager.agent_in_wrapup(AGENT_ID, wrapup_time)

        dao.agent.set_on_call_acd.assert_called_once_with(AGENT_ID, expected_on_call_acd)
        dao.agent.set_on_wrapup.assert_called_once_with(AGENT_ID, expected_in_wrapup)
        self.agent_availability_computer.compute.assert_called_once_with(AGENT_ID)

    def test_agent_in_wrapup_schedules_an_agent_completed(self):
        wrapup_time = 10
        self.agent_status_manager.agent_wrapup_completed = Mock()

        self.agent_status_manager.agent_in_wrapup(AGENT_ID, wrapup_time)
        self.task_scheduler.run(delta=wrapup_time + 1)

        self.agent_status_manager.agent_wrapup_completed.assert_called_once_with(AGENT_ID)

    def test_wrapup_tasks_are_removed_when_wrapup_goes_out(self):
        wrapup_time = 10

        self.agent_status_manager.agent_wrapup_completed = Mock()

        self.agent_status_manager.agent_in_wrapup(AGENT_ID, wrapup_time)
        self.agent_status_manager.agent_logged_out(AGENT_ID)

        self.task_scheduler.run(delta=wrapup_time + 1)

        assert_that(self.agent_status_manager.agent_wrapup_completed.call_count, equal_to(0))

    def test_agent_wrapup_completed(self):
        expected_in_wrapup = False

        self.agent_status_manager.agent_wrapup_completed(AGENT_ID)

        dao.agent.set_on_wrapup.assert_called_once_with(AGENT_ID, expected_in_wrapup)
        self.agent_availability_computer.compute.assert_called_once_with(AGENT_ID)


class TestAgentStatusManager(unittest.TestCase):

    def setUp(self):
        dao.agent = Mock(AgentDAO)
        self.agent_availability_computer = Mock(AgentAvailabilityComputer)
        dao.innerdata = Mock(InnerdataDAO)
        self.task_scheduler = Mock(task_scheduler._TaskScheduler)
        self.agent_status_manager = AgentStatusManager(self.agent_availability_computer, self.task_scheduler)

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

    def test_agent_paused_all(self):
        self.agent_status_manager.agent_paused_all(AGENT_ID)

        self.agent_availability_computer.compute.assert_called_once_with(AGENT_ID)

    def test_agent_unpaused(self):
        self.agent_status_manager.agent_unpaused(AGENT_ID)

        self.agent_availability_computer.compute.assert_called_once_with(AGENT_ID)
