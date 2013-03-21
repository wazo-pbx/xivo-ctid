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

from xivo_cti.services.agent_on_call_updater import AgentOnCallUpdater
from xivo_cti.services.agent.availability_updater import AgentAvailabilityUpdater
from xivo_cti.services.queue_member.member import QueueMemberState, QueueMember
from xivo_cti.services.agent.status_manager import AgentStatusManager
from xivo_cti import dao
from xivo_cti.dao.agent_dao import AgentDAO
from xivo_cti.services.queue_member.notifier import QueueMemberNotifier


class TestAgentStatusManager(unittest.TestCase):

    def setUp(self):
        dao.agent = Mock(AgentDAO)
        self.notifier = Mock(QueueMemberNotifier)
        self.call_updater = Mock(AgentOnCallUpdater)
        self.availability_updater = Mock(AgentAvailabilityUpdater)

    def test_manager_subscription(self):
        manager = AgentStatusManager(self.notifier, self.call_updater,
                                     self.availability_updater)
        manager.subscribe_to_queue_member()

        self.notifier.subscribe_to_queue_member_update.assert_called_once_with(ANY)

    def test_manager_when_agent_does_not_exist(self):
        member_state = QueueMemberState()
        member_state.status = 0
        member = QueueMember('queue1', 'Agent/12', member_state)

        dao.agent.get_id_from_interface.side_effect = [ValueError()]

        manager = AgentStatusManager(self.notifier, self.call_updater,
                                     self.availability_updater)
        manager.on_queue_member_update(member)

        self.assertEqual(self.availability_updater.agent_in_use.call_count, 0)
        self.assertEqual(self.call_updater.answered_call.call_count, 0)

    def test_manager_puts_agent_in_use(self):
        queue_name = 'queue1'
        member_name = 'Agent/12'
        agent_id = 12
        status = 2

        member_state = QueueMemberState()
        member_state.status = status
        member = QueueMember(queue_name, member_name, member_state)
        dao.agent.get_id_from_interface.return_value = agent_id

        manager = AgentStatusManager(self.notifier, self.call_updater,
                                     self.availability_updater)
        manager.on_queue_member_update(member)

        self.availability_updater.agent_in_use.assert_called_once_with(agent_id)
        self.call_updater.answered_call.assert_called_once_with(agent_id)

    def test_manager_completes_call(self):
        queue_name = 'queue1'
        member_name = 'Agent/12'
        agent_id = 12
        status = 1

        member_state = QueueMemberState()
        member_state.status = status
        member = QueueMember(queue_name, member_name, member_state)

        dao.agent.get_id_from_interface.return_value = agent_id

        manager = AgentStatusManager(self.notifier, self.call_updater,
                                     self.availability_updater)
        manager.on_queue_member_update(member)

        self.availability_updater.agent_call_completed.assert_called_once_with(agent_id, 0)
        self.call_updater.call_completed.assert_called_once_with(agent_id)