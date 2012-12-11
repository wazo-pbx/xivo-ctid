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

    def test_queue_add(self):
        queue_name = 'accueil'
        interface = 'Agent/1234'
        paused = False
        skills = ''

        self.executor.queue_add(queue_name, interface, paused, skills)

        self.assertEqual(self.ami.method_calls, [call.queueadd(queue_name, interface, paused, skills)])

    def test_queue_remove(self):
        queue_name = 'accueil'
        interface = 'Agent/1234'

        self.executor.queue_remove(queue_name, interface)

        self.assertEqual(self.ami.method_calls, [call.queueremove(queue_name, interface)])

    def test_queues_pause(self):
        interface = 'Agent/1234'

        self.executor.queues_pause(interface)

        self.assertEqual(self.ami.method_calls, [call.queuepauseall(interface, 'True')])

    def test_queues_unpause(self):
        interface = 'Agent/1234'

        self.executor.queues_unpause(interface)

        self.assertEqual(self.ami.method_calls, [call.queuepauseall(interface, 'False')])

    def test_queue_pause(self):
        queue_name = 'accueil'
        interface = 'Agent/1234'

        self.executor.queue_pause(queue_name, interface)

        self.assertEqual(self.ami.method_calls, [call.queuepause(queue_name, interface, 'True')])

    def test_queue_unpause(self):
        queue_name = 'accueil'
        interface = 'Agent/1234'

        self.executor.queue_unpause(queue_name, interface)

        self.assertEqual(self.ami.method_calls, [call.queuepause(queue_name, interface, 'False')])

    def test_logoff(self):
        agent_id = 1234

        self.executor.logoff(agent_id)

        self.agent_client.logoff_agent.assert_called_once_with(agent_id)

    def test_log_presence(self):
        presence = 'disconnected'
        agent_interface = 'Agent/3135'

        self.executor.log_presence(agent_interface, presence)

        self.ami.queuelog.assert_called_once_with('NONE', 'PRESENCE', interface=agent_interface, message=presence)
