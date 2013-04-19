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

from xivo_cti.services.agent.availability_updater import AgentAvailabilityUpdater
from xivo_cti.services.queue_member.member import QueueMemberState, QueueMember
from xivo_cti.services.agent.status_manager import AgentStatusManager, \
    QueueEventReceiver, parse_ami_call_completed
from xivo_cti import dao
from xivo_cti.dao.agent_dao import AgentDAO
from xivo_cti.services.queue_member.notifier import QueueMemberNotifier


class TestAmiEventCallbackes(unittest.TestCase):

    def setUp(self):
        dao.agent = Mock(AgentDAO)
        self.manager = Mock(AgentStatusManager)

    def test_parse_ami_call_completed_no_wrapup(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1000', 'WrapupTime': '0'}

        dao.agent.get_id_from_interface.return_value = agent_id

        parse_ami_call_completed(ami_event, self.manager)
        self.assertEquals(self.manager.agent_in_wrapup.call_count, 0)

    def test_parse_ami_call_completed_with_wrapup(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1000', 'WrapupTime': '10'}

        dao.agent.get_id_from_interface.return_value = agent_id

        parse_ami_call_completed(ami_event, self.manager)
        self.manager.agent_in_wrapup.assert_called_once_with(agent_id, 10)

    def test_parse_ami_call_completed_no_agent(self):
        ami_event = {'MemberName': 'SIP/abc', 'WrapupTime': '10'}

        dao.agent.get_id_from_interface.side_effect = [ValueError()]

        parse_ami_call_completed(ami_event, self.manager)
        self.assertEquals(self.manager.agent_in_wrapup.call_count, 0)


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

        self.assertEqual(self.status_manager.agent_in_use.call_count, 0)

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

        self.status_manager.agent_in_use.assert_called_once_with(agent_id)

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

        self.status_manager.agent_not_in_use.assert_called_once_with(agent_id)


class TestAgentStatusManager(unittest.TestCase):

    def setUp(self):
        dao.agent = Mock(AgentDAO)
        self.availability_updater = Mock(AgentAvailabilityUpdater)

    def test_agent_in_use_updates_availability(self):
        dao.agent.on_call.return_value = False
        agent_id = 12

        manager = AgentStatusManager(self.availability_updater)
        manager.agent_in_use(agent_id)

        dao.agent.on_call.assert_called_once_with(agent_id)
        dao.agent.set_on_call.assert_called_once_with(agent_id, True)
        self.availability_updater.agent_in_use.assert_called_once_with(agent_id)

    def test_agent_in_use_does_not_update_if_already_in_use(self):
        dao.agent.on_call.return_value = True
        agent_id = 12

        manager = AgentStatusManager(self.availability_updater)
        manager.agent_in_use(agent_id)

        dao.agent.on_call.assert_called_once_with(agent_id)
        self.assertEquals(self.availability_updater.agent_in_use.call_count, 0)
        self.assertEquals(dao.agent.set_on_call.call_count, 0)

    def test_agent_not_in_use_updates_availability(self):
        dao.agent.on_call.return_value = True
        agent_id = 12

        manager = AgentStatusManager(self.availability_updater)
        manager.agent_not_in_use(agent_id)

        dao.agent.on_call.assert_called_once_with(agent_id)
        dao.agent.set_on_call.assert_called_once_with(agent_id, False)
        self.availability_updater.agent_not_in_use.assert_called_once_with(agent_id)

    def test_agent_not_in_use_does_not_update_if_already_not_in_use(self):
        dao.agent.on_call.return_value = False
        agent_id = 12

        manager = AgentStatusManager(self.availability_updater)
        manager.agent_not_in_use(agent_id)

        dao.agent.on_call.assert_called_once_with(agent_id)
        self.assertEquals(self.availability_updater.agent_not_in_use.call_count, 0)
        self.assertEquals(dao.agent.set_on_call.call_count, 0)

    def test_agent_in_wrapup_updates_availability(self):
        agent_id = 12
        wrapup = 10

        manager = AgentStatusManager(self.availability_updater)
        manager.agent_in_wrapup(agent_id, wrapup)

        dao.agent.set_on_wrapup.assert_called_once_with(agent_id, True)
        self.availability_updater.agent_in_wrapup.assert_called_once_with(agent_id, wrapup)
