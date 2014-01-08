# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from xivo_cti.services.queue_member import common


class TestQueueMemberNotifier(unittest.TestCase):

    def test_format_member_name_of_agent(self):
        agent_number = '1234'

        member_name = common.format_member_name_of_agent(agent_number)

        self.assertEqual(member_name, 'Agent/1234')

    def test_format_queue_member_id(self):
        queue_name = 'queue1'
        member_name = 'Agent/42'

        queue_member_id = common.format_queue_member_id(queue_name, member_name)

        self.assertEqual(queue_member_id, 'Agent/42,queue1')

    def test_is_agent_member_name_when_it_is(self):
        member_name = 'Agent/42'

        result = common.is_agent_member_name(member_name)

        self.assertTrue(result)

    def test_is_agent_member_name_when_it_is_not(self):
        member_name = 'SIP/abcdef'

        result = common.is_agent_member_name(member_name)

        self.assertFalse(result)
