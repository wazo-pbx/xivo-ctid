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
from mock import Mock, ANY
from hamcrest import *

from xivo_cti.services.agent import status_manager
from xivo_cti.services.agent.availability_updater import AgentAvailabilityUpdater
from xivo_cti.services.queue_member.member import QueueMemberState, QueueMember
from xivo_cti.services.agent.status_manager import AgentStatusManager, \
    QueueEventReceiver
from xivo_cti import dao
from xivo_cti.dao.agent_dao import AgentDAO
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.scheduler import Scheduler
from xivo_cti.dao.innerdata_dao import InnerdataDAO
from xivo_cti.services.queue_member.notifier import QueueMemberNotifier


class TestParseAmi(unittest.TestCase):

    def setUp(self):
        dao.agent = Mock(AgentDAO)
        self.manager = Mock(AgentStatusManager)

    def test_parse_ami_login(self):
        agent_id = 12
        ami_event = {'AgentID': agent_id,
                     'Event': 'UserEvent',
                     'UserEvent': 'AgentLogin'}
        dao.agent.get_id_from_number.return_value = agent_id

        status_manager.parse_ami_login(ami_event, self.manager)

        self.manager.agent_logged_in.assert_called_once_with(agent_id)

    def test_parse_ami_logout(self):
        agent_id = 12
        ami_event = {'AgentID': agent_id,
                     'Event': 'UserEvent',
                     'UserEvent': 'AgentLogoff'}
        dao.agent.get_id_from_number.return_value = agent_id

        status_manager.parse_ami_logout(ami_event, self.manager)

        self.manager.agent_logged_out.assert_called_once_with(agent_id)

    def test_parse_ami_paused_partially(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1234',
                     'Event': 'QueueMemberPaused',
                     'Queue': 'q01',
                     'Paused': '1'}
        dao.agent.get_id_from_interface.return_value = agent_id
        dao.agent.is_completely_paused.return_value = False

        status_manager.parse_ami_paused(ami_event, self.manager)

        self.assertEqual(self.manager.agent_paused_all.call_count, 0)

    def test_parse_ami_paused_completely(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1234',
                     'Event': 'QueueMemberPaused',
                     'Queue': 'q01',
                     'Paused': '1'}
        dao.agent.get_id_from_interface.return_value = agent_id
        dao.agent.is_completely_paused.return_value = True

        status_manager.parse_ami_paused(ami_event, self.manager)

        self.manager.agent_paused_all.assert_called_once_with(agent_id)

    def test_parse_ami_paused_not_an_agent(self):
        ami_event = {'MemberName': 'SIP/abcdef',
                     'Event': 'QueueMemberPaused',
                     'Queue': 'q01',
                     'Paused': '1'}
        dao.agent.get_id_from_interface.side_effect = ValueError()

        status_manager.parse_ami_paused(ami_event, self.manager)

        self.assertFalse(self.manager.agent_paused_all.called)
        self.assertFalse(self.manager.agent_unpaused.called)

    def test_parse_ami_unpaused(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1234',
                     'Event': 'QueueMemberPaused',
                     'Queue': 'q01',
                     'Paused': '0'}
        dao.agent.get_id_from_interface.return_value = agent_id

        status_manager.parse_ami_paused(ami_event, self.manager)

        self.manager.agent_unpaused.assert_called_once_with(agent_id)

    def test_parse_ami_acd_call_end_no_wrapup(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1000', 'WrapupTime': '0'}
        dao.agent.get_id_from_interface.return_value = agent_id

        status_manager.parse_ami_acd_call_end(ami_event, self.manager)

        self.assertEquals(self.manager.agent_in_wrapup.call_count, 0)
        self.manager.acd_call_end.called_once_with(agent_id)

    def test_parse_ami_acd_call_end_with_wrapup(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1000', 'WrapupTime': '10'}
        dao.agent.get_id_from_interface.return_value = agent_id

        status_manager.parse_ami_acd_call_end(ami_event, self.manager)

        self.manager.agent_in_wrapup.assert_called_once_with(agent_id, 10)
        self.assertEqual(self.manager.acd_call_end.call_count, 0)

    def test_parse_ami_acd_call_end_no_agent(self):
        ami_event = {'MemberName': 'SIP/abc', 'WrapupTime': '10'}
        dao.agent.get_id_from_interface.side_effect = ValueError()

        status_manager.parse_ami_acd_call_end(ami_event, self.manager)

        self.assertEquals(self.manager.agent_in_wrapup.call_count, 0)
        self.assertEqual(self.manager.acd_call_end.call_count, 0)


class TestQueueEventReceiver(unittest.TestCase):

    def setUp(self):
        dao.agent = Mock(AgentDAO)
        self.notifier = Mock(QueueMemberNotifier)
        self.status_manager = Mock(AgentStatusManager)

    def test_subscription(self):
        receiver = QueueEventReceiver(self.notifier, self.status_manager)
        receiver.subscribe()

        self.notifier.subscribe_to_queue_member_update.assert_called_once_with(ANY)

    def test_receiver_when_agent_does_not_exist(self):
        member_state = QueueMemberState()
        member_state.status = 0
        member = QueueMember('queue1', 'Agent/12', member_state)

        dao.agent.get_id_from_interface.side_effect = [ValueError()]

        receiver = QueueEventReceiver(self.notifier, self.status_manager)
        receiver.on_queue_member_update(member)

        self.assertEquals(self.status_manager.agent_in_use.call_count, 0)

    def test_manager_puts_agent_in_use(self):
        queue_name = 'queue1'
        member_name = 'Agent/12'
        agent_id = 12
        status = 2

        member_state = QueueMemberState()
        member_state.status = status
        member = QueueMember(queue_name, member_name, member_state)
        dao.agent.get_id_from_interface.return_value = agent_id

        receiver = QueueEventReceiver(self.notifier, self.status_manager)
        receiver.on_queue_member_update(member)

        self.status_manager.device_in_use.assert_called_once_with(agent_id)

    def test_manager_completes_call(self):
        queue_name = 'queue1'
        member_name = 'Agent/12'
        agent_id = 12
        status = 1

        member_state = QueueMemberState()
        member_state.status = status
        member = QueueMember(queue_name, member_name, member_state)

        dao.agent.get_id_from_interface.return_value = agent_id

        receiver = QueueEventReceiver(self.notifier, self.status_manager)
        receiver.on_queue_member_update(member)

        self.status_manager.device_not_in_use.assert_called_once_with(agent_id)


class TestAgentStatusManager(unittest.TestCase):

    def setUp(self):
        dao.agent = Mock(AgentDAO)
        self.agent_availability_updater = Mock(AgentAvailabilityUpdater)
        dao.innerdata = Mock(InnerdataDAO)
        self.agent_status_manager = AgentStatusManager(self.agent_availability_updater, Mock(Scheduler))

    def test_agent_logged_in(self):
        dao.agent.is_completely_paused.return_value = False

        agent_id = 12

        self.agent_status_manager.agent_logged_in(agent_id)

        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.available)

    def test_agent_logged_in_paused(self):
        dao.agent.is_completely_paused.return_value = True

        agent_id = 12

        self.agent_status_manager.agent_logged_in(agent_id)

        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.unavailable)

    def test_agent_logged_out(self):
        agent_id = 12

        self.agent_status_manager.agent_logged_out(agent_id)

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

    def test_device_in_use_when_wrapup(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = True
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_nonacd.return_value = False
        dao.agent.on_call_acd.return_value = False

        self.agent_status_manager.device_in_use(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_device_in_use_when_paused(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = False
        dao.agent.is_completely_paused.return_value = True
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_nonacd.return_value = False
        dao.agent.on_call_acd.return_value = False

        self.agent_status_manager.device_in_use(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_device_in_use_when_unlogged(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = False
        dao.agent.on_call_nonacd.return_value = False
        dao.agent.on_call_acd.return_value = False

        self.agent_status_manager.device_in_use(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_device_in_use_when_on_call_nonacd(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_nonacd.return_value = True
        dao.agent.on_call_acd.return_value = False

        self.agent_status_manager.device_in_use(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_device_in_use_when_on_call_acd(self):
        agent_id = 12
        dao.agent.on_wrapup.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_call_nonacd.return_value = False
        dao.agent.on_call_acd.return_value = True

        self.agent_status_manager.device_in_use(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_agent_in_use(self):
        dao.agent.on_call.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_in_use(agent_id)

        dao.agent.on_call.assert_called_once_with(agent_id)
        dao.agent.set_on_call.assert_called_once_with(agent_id, True)

        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.unavailable)

    def test_agent_in_use_when_already_in_use(self):
        dao.agent.on_call.return_value = True
        agent_id = 12

        self.agent_status_manager.agent_in_use(agent_id)

        dao.agent.on_call.assert_called_once_with(agent_id)
        self.assertEquals(dao.agent.set_on_call.call_count, 0)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_agent_not_in_use(self):
        dao.agent.on_call.return_value = True
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_wrapup.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_not_in_use(agent_id)

        dao.agent.on_call.assert_called_once_with(agent_id)
        dao.agent.set_on_call.assert_called_once_with(agent_id, False)
        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.available)

    def test_agent_not_in_use_when_already_not_in_use(self):
        dao.agent.on_call.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_wrapup.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_not_in_use(agent_id)

        dao.agent.on_call.assert_called_once_with(agent_id)
        self.assertEquals(dao.agent.set_on_call.call_count, 0)
        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_agent_not_in_use_logged_out(self):
        dao.agent.on_call.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = False
        dao.agent.on_wrapup.return_value = False

        agent_id = 12

        self.agent_status_manager.agent_not_in_use(agent_id)

        self.assertEquals(dao.agent.set_on_call.call_count, 0)
        self.assertEquals(self.agent_status_manager.scheduler.schedule.call_count, 0)
        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_agent_not_in_use_paused(self):
        dao.agent.on_call.return_value = False
        dao.agent.is_completely_paused.return_value = True
        dao.agent.is_logged.return_value = True
        dao.agent.on_wrapup.return_value = False

        agent_id = 12

        self.agent_status_manager.agent_not_in_use(agent_id)

        self.assertEquals(dao.agent.set_on_call.call_count, 0)
        self.assertEquals(self.agent_status_manager.scheduler.schedule.call_count, 0)
        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_agent_not_in_use_on_wrapup(self):
        dao.agent.on_call.return_value = False
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_wrapup.return_value = True

        agent_id = 12

        self.agent_status_manager.agent_not_in_use(agent_id)

        self.assertEquals(dao.agent.set_on_call.call_count, 0)
        self.assertEquals(self.agent_status_manager.scheduler.schedule.call_count, 0)
        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_agent_in_wrapup(self):
        agent_id = 12
        wrapup_time = 25

        self.agent_status_manager.agent_in_wrapup(agent_id, wrapup_time)

        dao.agent.set_on_wrapup.assert_called_once_with(agent_id, True)
        self.agent_status_manager.scheduler.schedule.assert_called_once_with(
            wrapup_time,
            self.agent_status_manager.agent_wrapup_completed,
            agent_id
        )
        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

    def test_agent_wrapup_completed(self):
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_call.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_wrapup_completed(agent_id)

        dao.agent.set_on_wrapup.assert_called_once_with(agent_id, False)
        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.available)

    def test_agent_wrapup_completed_in_pause(self):
        dao.agent.is_completely_paused.return_value = True
        dao.agent.is_logged.return_value = True
        dao.agent.on_call.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_wrapup_completed(agent_id)

        dao.agent.set_on_wrapup.assert_called_once_with(agent_id, False)
        self.assertEquals(self.agent_availability_updater.update.call_count, 0)


    def test_agent_wrapup_completed_logged_out(self):
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = False
        dao.agent.on_call.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_wrapup_completed(agent_id)

        dao.agent.set_on_wrapup.assert_called_once_with(agent_id, False)
        self.assertEquals(self.agent_availability_updater.update.call_count, 0)


    def test_agent_wrapup_completed_in_conversation(self):
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True
        dao.agent.on_call.return_value = True
        agent_id = 12

        self.agent_status_manager.agent_wrapup_completed(agent_id)

        dao.agent.set_on_wrapup.assert_called_once_with(agent_id, False)
        self.assertEquals(dao.innerdata.set_agent_availability.call_count, 0)
        self.assertEquals(self.agent_availability_updater.update.call_count, 0)


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
        dao.agent.on_call.return_value = False
        dao.agent.on_wrapup.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_unpaused(agent_id)

        self.agent_availability_updater.update.assert_called_once_with(agent_id, AgentStatus.available)

    def test_agent_unpaused_calling(self):
        dao.agent.is_logged.return_value = True
        dao.agent.on_call.return_value = True
        dao.agent.on_wrapup.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_unpaused(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)


    def test_agent_unpaused_while_unlogged(self):
        dao.agent.is_logged.return_value = False
        dao.agent.on_call.return_value = False
        dao.agent.on_wrapup.return_value = False
        agent_id = 12

        self.agent_status_manager.agent_unpaused(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)


    def test_agent_unpaused_on_wrapup(self):
        dao.agent.is_logged.return_value = True
        dao.agent.on_call.return_value = False
        dao.agent.on_wrapup.return_value = True
        agent_id = 12

        self.agent_status_manager.agent_unpaused(agent_id)

        self.assertEquals(self.agent_availability_updater.update.call_count, 0)

