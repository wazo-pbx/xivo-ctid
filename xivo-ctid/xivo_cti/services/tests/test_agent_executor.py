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
# contracted with Avencall. See the LICENSE file at top of the souce tree
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
from tests.mock import Mock, call
from xivo_cti.services.agent_executor import AgentExecutor
from xivo_cti.xivo_ami import AMIClass


class TestAgentExecutor(unittest.TestCase):

    def setUp(self):
        self.agent_client = Mock()
        ami_class = Mock(AMIClass)
        self.executor = AgentExecutor(self.agent_client, ami_class)
        self.ami = Mock(AMIClass)
        self.executor.ami = self.ami

    def test_add_to_queue(self):
        agent_id = 42
        queue_id = 1

        self.executor.add_to_queue(agent_id, queue_id)

        self.agent_client.add_agent_to_queue.assert_called_once_with(agent_id, queue_id)

    def test_remove_from_queue(self):
        agent_id = 42
        queue_id = 1

        self.executor.remove_from_queue(agent_id, queue_id)

        self.agent_client.remove_agent_from_queue.assert_called_once_with(agent_id, queue_id)

    def test_pause_on_queue(self):
        queue_name = 'accueil'
        interface = 'SIP/abcdef'

        self.executor.pause_on_queue(interface, queue_name)

        self.assertEqual(self.ami.method_calls, [call.queuepause(queue_name, interface, 'True')])

    def test_pause_on_all_queues(self):
        interface = 'SIP/abcdef'

        self.executor.pause_on_all_queues(interface)

        self.assertEqual(self.ami.method_calls, [call.queuepauseall(interface, 'True')])

    def test_unpause_on_queue(self):
        queue_name = 'accueil'
        interface = 'SIP/abcdef'

        self.executor.unpause_on_queue(interface, queue_name)

        self.assertEqual(self.ami.method_calls, [call.queuepause(queue_name, interface, 'False')])

    def test_unpause_on_all_queues(self):
        interface = 'SIP/abcdef'

        self.executor.unpause_on_all_queues(interface)

        self.assertEqual(self.ami.method_calls, [call.queuepauseall(interface, 'False')])

    def test_logoff(self):
        agent_id = 1234

        self.executor.logoff(agent_id)

        self.agent_client.logoff_agent.assert_called_once_with(agent_id)

    def test_log_presence(self):
        presence = 'disconnected'
        agent_interface = 'Agent/3135'

        self.executor.log_presence(agent_interface, presence)

        self.ami.queuelog.assert_called_once_with('NONE', 'PRESENCE', interface=agent_interface, message=presence)
