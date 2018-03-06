# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock
from xivo_cti.ami.ami_agent_login_logoff import AMIAgentLoginLogoff
from xivo_cti.statistics.queue_statistics_producer import QueueStatisticsProducer


class TestAMIAgentLoginLogoff(unittest.TestCase):

    def setUp(self):
        self.ami_agent_login_logoff = AMIAgentLoginLogoff()
        self.queue_statistics_producer = Mock(QueueStatisticsProducer)
        self.ami_agent_login_logoff.queue_statistics_producer = self.queue_statistics_producer

    def test_receive_event_agentlogin(self):
        event = {'AgentNumber': '22011'}

        self.ami_agent_login_logoff.on_event_agent_login(event)

        self.queue_statistics_producer.on_agent_loggedon.assert_called_with('Agent/22011')

    def test_receive_event_agentlogoff(self):
        event = {'AgentNumber': '22011'}

        self.ami_agent_login_logoff.on_event_agent_logoff(event)

        self.queue_statistics_producer.on_agent_loggedoff.assert_called_with('Agent/22011')
