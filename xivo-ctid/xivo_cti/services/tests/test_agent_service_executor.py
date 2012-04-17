#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2011  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
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
from xivo_cti.services.agent_service_executor import AgentServiceExecutor

class TestAgentServiceExecutor(unittest.TestCase):

    def setUp(self):
        self.executor = AgentServiceExecutor()
        self.interface_ami = Mock()
        self.executor.interface_ami = self.interface_ami

    def test_build_pause_params(self):
        interface = 'Agent/1234'
        pausestate = True
        expected_result = {'mode': 'pause',
                         'amicommand': 'sendcommand',
                         'amiargs': ('queuepause',
                             [('Interface', interface),
                              ('Paused', 'True')])
                   }

        result = self.executor._build_pause_params(interface, pausestate)

        self.assertEqual(result, expected_result)

    def test_queues_pause(self):
        interface = 'Agent/1234'
        expected_params = self.executor._build_pause_params(interface, True)

        self.executor.queues_pause(interface)

        self.assertEqual(self.interface_ami.method_calls, [call.execute_and_track('', expected_params)])

    def test_queues_unpause(self):
        interface = 'Agent/1234'
        expected_params = self.executor._build_pause_params(interface, False)

        self.executor.queues_unpause(interface)

        self.assertEqual(self.interface_ami.method_calls, [call.execute_and_track('', expected_params)])
