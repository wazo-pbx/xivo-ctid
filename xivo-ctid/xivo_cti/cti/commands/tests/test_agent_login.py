# vim: set fileencoding=utf-8 :
# XiVO CTI Server

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
from xivo_cti.cti.commands.agent_login import AgentLogin


class TestAgentLogin(unittest.TestCase):

    def setUp(self):
        self.agent_id = '5'
        self.number = '6666'
        self.agent_dict = {'commandid': 1588880676,
                           'command': 'agentlogin',
                           'class': 'ipbxcommand',
                           'agentphonenumber': self.number,
                           'agentids': self.agent_id}

    def test_agent_login_with_number(self):
        agent_login = AgentLogin.from_dict(self.agent_dict)

        self.assertEqual(agent_login.agent_phone_number, self.number)
        self.assertEqual(agent_login.agent_id, self.agent_id)

    def test_agent_login_no_number(self):
        self.agent_dict.pop('agentphonenumber')

        agent_login = AgentLogin.from_dict(self.agent_dict)

        self.assertEqual(agent_login.agent_phone_number, None)
        self.assertEqual(agent_login.agent_id, self.agent_id)
