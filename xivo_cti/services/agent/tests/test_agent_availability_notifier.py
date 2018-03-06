# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock, patch
from xivo_cti.services.agent.availability_notifier import AgentAvailabilityNotifier
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.ctiserver import CTIServer


class TestAgentAvailabilityNotifier(unittest.TestCase):

    def setUp(self):
        self.cti_server = Mock(CTIServer)
        self.availability_notifier = AgentAvailabilityNotifier(self.cti_server)

    @patch('xivo_cti.services.agent.availability_notifier.CTIMessageFormatter')
    @patch('xivo_cti.dao.agent')
    def test_notify(self, agent_dao, message_formatter):
        agent_id = 42
        new_agent_status = {
            'availability': AgentStatus.logged_out,
            'availability_since': 123456789
        }
        agent_dao.agent_status.return_value = new_agent_status
        cti_message = {
            'class': 'getlist',
            'listname': 'agents',
            'function': 'updatestatus',
            'tipbxid': 'xivo',
            'tid': agent_id,
            'status': new_agent_status
        }
        message_formatter.update_agent_status.return_value = cti_message

        self.availability_notifier.notify(agent_id)

        message_formatter.update_agent_status.assert_called_once_with(agent_id,
                                                                      new_agent_status)
        self.cti_server.send_cti_event.assert_called_once_with(cti_message)
