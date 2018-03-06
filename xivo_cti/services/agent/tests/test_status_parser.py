# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_cti import dao
from xivo_cti.dao.agent_dao import AgentDAO
from xivo_cti.services.agent.status_adapter import AgentStatusAdapter
from xivo_cti.services.agent.status_parser import AgentStatusParser
from xivo_cti.services.agent.status_manager import AgentStatusManager


class TestAgentStatusParser(unittest.TestCase):

    def setUp(self):
        dao.agent = Mock(AgentDAO)
        self.manager = Mock(AgentStatusManager)
        self.adapter = Mock(AgentStatusAdapter)
        self.parser = AgentStatusParser(self.manager, self.adapter)

    def test_parse_ami_login(self):
        agent_id = 12
        ami_event = {'AgentID': agent_id,
                     'Event': 'UserEvent',
                     'UserEvent': 'AgentLogin'}
        dao.agent.get_id_from_number.return_value = agent_id

        self.parser.parse_ami_login(ami_event)

        self.manager.agent_logged_in.assert_called_once_with(agent_id)
        self.adapter.subscribe_to_agent_events.assert_called_once_with(agent_id)

    def test_parse_ami_logout(self):
        agent_id = 12
        ami_event = {'AgentID': agent_id,
                     'Event': 'UserEvent',
                     'UserEvent': 'AgentLogoff'}
        dao.agent.get_id_from_number.return_value = agent_id

        self.parser.parse_ami_logout(ami_event)

        self.manager.agent_logged_out.assert_called_once_with(agent_id)
        self.adapter.unsubscribe_from_agent_events.assert_called_once_with(agent_id)

    def test_parse_ami_paused_partially(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1234',
                     'Event': 'QueueMemberPause',
                     'Queue': 'q01',
                     'Paused': '1'}
        dao.agent.get_id_from_interface.return_value = agent_id
        dao.agent.is_completely_paused.return_value = False

        self.parser.parse_ami_paused(ami_event)

        self.assertEqual(self.manager.agent_paused_all.call_count, 0)

    def test_parse_ami_paused_completely(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1234',
                     'Event': 'QueueMemberPause',
                     'Queue': 'q01',
                     'Paused': '1'}
        dao.agent.get_id_from_interface.return_value = agent_id
        dao.agent.is_completely_paused.return_value = True

        self.parser.parse_ami_paused(ami_event)

        self.manager.agent_paused_all.assert_called_once_with(agent_id)

    def test_parse_ami_paused_not_an_agent(self):
        ami_event = {'MemberName': 'SIP/abcdef',
                     'Event': 'QueueMemberPause',
                     'Queue': 'q01',
                     'Paused': '1'}
        dao.agent.get_id_from_interface.side_effect = ValueError()

        self.parser.parse_ami_paused(ami_event)

        self.assertFalse(self.manager.agent_paused_all.called)
        self.assertFalse(self.manager.agent_unpaused.called)

    def test_parse_ami_unpaused(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1234',
                     'Event': 'QueueMemberPause',
                     'Queue': 'q01',
                     'Paused': '0'}
        dao.agent.get_id_from_interface.return_value = agent_id

        self.parser.parse_ami_paused(ami_event)

        self.manager.agent_unpaused.assert_called_once_with(agent_id)

    def test_parse_ami_acd_call_start(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1000'}
        dao.agent.get_id_from_interface.return_value = agent_id

        self.parser.parse_ami_acd_call_start(ami_event)

        self.manager.acd_call_start.called_once_with(agent_id)

    def test_parse_ami_acd_call_start_no_agent(self):
        ami_event = {'MemberName': 'SIP/abc'}
        dao.agent.get_id_from_interface.side_effect = ValueError()

        self.parser.parse_ami_acd_call_start(ami_event)

        self.assertEqual(self.manager.acd_call_start.call_count, 0)

    def test_parse_ami_acd_call_end_no_wrapup(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1000', 'WrapupTime': '0'}
        dao.agent.get_id_from_interface.return_value = agent_id

        self.parser.parse_ami_acd_call_end(ami_event)

        self.assertEquals(self.manager.agent_in_wrapup.call_count, 0)
        self.manager.acd_call_end.called_once_with(agent_id)

    def test_parse_ami_acd_call_end_with_wrapup(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1000', 'WrapupTime': '10'}
        dao.agent.get_id_from_interface.return_value = agent_id

        self.parser.parse_ami_acd_call_end(ami_event)

        self.manager.agent_in_wrapup.assert_called_once_with(agent_id, 10)
        self.assertEqual(self.manager.acd_call_end.call_count, 0)

    def test_parse_ami_acd_call_end_no_agent(self):
        ami_event = {'MemberName': 'SIP/abc', 'WrapupTime': '10'}
        dao.agent.get_id_from_interface.side_effect = ValueError()

        self.parser.parse_ami_acd_call_end(ami_event)

        self.assertEquals(self.manager.agent_in_wrapup.call_count, 0)
        self.assertEqual(self.manager.acd_call_end.call_count, 0)
