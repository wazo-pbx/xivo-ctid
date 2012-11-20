# -*- coding: utf-8 -*-

# Copyright (C) 2007-2012  Avencall

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
from mock import Mock
from xivo_cti import innerdata
from xivo_cti.dao.queue_member_dao import QueueMemberDAO


class TestQueueMemberDAO(unittest.TestCase):
    def setUp(self):
        self.innerdata = Mock(innerdata.Safe)

    def test_get_queue_count_for_agent(self):
        agent_interface = 'Agent/1234'
        expected_result = 2
        self.innerdata.queuemembers_config = {
            'queue_name_1,Agent/1234': {
                'paused': '1',
                'interface': 'Agent/1234',
            },
            'queue_name_2,Agent/1234': {
                'paused': '0',
                'interface': 'Agent/1234',
            },
            'queue_name_3,Agent/5678': {
                'paused': '0',
                'interface': 'Agent/5678',
            },
        }
        queue_member_dao = QueueMemberDAO(self.innerdata)

        result = queue_member_dao.get_queue_count_for_agent(agent_interface)

        self.assertEqual(result, expected_result)

    def test_get_paused_count_for_agent(self):
        agent_interface = 'Agent/1234'
        expected_result = 1
        self.innerdata.queuemembers_config = {
            'queue_name_1,Agent/1234': {
                'paused': '0',
                'interface': 'Agent/1234',
            },
            'queue_name_2,Agent/1234': {
                'paused': '1',
                'interface': 'Agent/1234',
            },
            'queue_name_3,Agent/5678': {
                'paused': '0',
                'interface': 'Agent/5678',
            },
            'queue_name_3,Agent/5678': {
                'paused': '1',
                'interface': 'Agent/5678',
            },
        }
        queue_member_dao = QueueMemberDAO(self.innerdata)

        result = queue_member_dao.get_paused_count_for_agent(agent_interface)

        self.assertEqual(result, expected_result)
