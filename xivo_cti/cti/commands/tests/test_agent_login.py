# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
