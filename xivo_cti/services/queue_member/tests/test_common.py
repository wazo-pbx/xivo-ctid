# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
