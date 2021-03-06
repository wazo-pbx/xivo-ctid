# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, call

from xivo_agentd_client import error
from xivo_agentd_client.error import AgentdClientError

from xivo_cti.exception import ExtensionInUseError, NoSuchExtensionError
from xivo_cti.services.agent.executor import AgentExecutor
from xivo_cti.xivo_ami import AMIClass


class TestAgentExecutor(unittest.TestCase):

    def setUp(self):
        self.agentd_client = Mock()
        ami_class = Mock(AMIClass)
        self.executor = AgentExecutor(self.agentd_client, ami_class)
        self.ami = Mock(AMIClass)
        self.executor.ami = self.ami

    def test_login_does_nothing_when_agent_is_already_logged(self):
        agent_id = 42
        exten = '1001'
        context = 'default'
        self.agentd_client.agents.login_agent.side_effect = AgentdClientError(error.ALREADY_LOGGED)

        self.executor.login(agent_id, exten, context)

    def test_login_raise_extension_in_use_when_extension_in_use(self):
        agent_id = 42
        exten = '1001'
        context = 'default'
        self.agentd_client.agents.login_agent.side_effect = AgentdClientError(error.ALREADY_IN_USE)

        self.assertRaises(ExtensionInUseError, self.executor.login, agent_id, exten, context)

    def test_login_raise_no_such_extension_when_no_such_extension(self):
        agent_id = 42
        exten = '1001'
        context = 'default'
        self.agentd_client.agents.login_agent.side_effect = AgentdClientError(error.NO_SUCH_EXTEN)

        self.assertRaises(NoSuchExtensionError, self.executor.login, agent_id, exten, context)

    def test_logoff(self):
        agent_id = 1234

        self.executor.logoff(agent_id)

        self.agentd_client.agents.logoff_agent.assert_called_once_with(agent_id)

    def test_add_to_queue(self):
        agent_id = 42
        queue_id = 1

        self.executor.add_to_queue(agent_id, queue_id)

        self.agentd_client.agents.add_agent_to_queue.assert_called_once_with(agent_id, queue_id)

    def test_remove_from_queue(self):
        agent_id = 42
        queue_id = 1

        self.executor.remove_from_queue(agent_id, queue_id)

        self.agentd_client.agents.remove_agent_from_queue.assert_called_once_with(agent_id, queue_id)

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

    def test_log_presence(self):
        presence = 'disconnected'
        agent_interface = 'Agent/3135'

        self.executor.log_presence(agent_interface, presence)

        self.ami.queuelog.assert_called_once_with('NONE', 'PRESENCE', interface=agent_interface, message=presence)
