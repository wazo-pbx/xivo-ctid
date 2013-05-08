# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from mock import Mock, call
from xivo_cti import innerdata
from xivo_cti.dao.agent_dao import notify_clients, AgentDAO
from xivo_cti.services.queue_member.manager import QueueMemberManager
from xivo_cti.services.agent.status import AgentStatus

class TestNotifyClients(unittest.TestCase):

    def setUp(self):
        self.innerdata = Mock(innerdata.Safe)
        self.queue_member_manager = Mock(QueueMemberManager)
        self.agent_dao = AgentDAO(self.innerdata, self.queue_member_manager)

    def test_notify_clients(self):
        class DecorateMe(object):
            def __init__(self, innerdata):
                self.innerdata = innerdata
                self.count = 0
                self.agent_id = None

            @notify_clients
            def decorate_me(self, agent_id):
                self.count += 1
                self.agent_id = agent_id

        agent_id = '42'

        d = DecorateMe(self.innerdata)
        d.decorate_me(agent_id)

        self.assertEqual(d.count,1)
        self.assertEqual(d.agent_id,agent_id)
        expected = [call('setforce', ('agents', 'updatestatus', agent_id)), call('empty_stack')]
        arg_list = self.innerdata.handle_cti_stack.call_args_list
        self.assertEqual(arg_list,expected)

class TestAgentDAO(unittest.TestCase):

    def setUp(self):
        self.innerdata = Mock(innerdata.Safe)
        self.queue_member_manager = Mock(QueueMemberManager)
        self.agent_dao = AgentDAO(self.innerdata, self.queue_member_manager)

    def test_get_id_from_interface(self):
        agent_number = '1234'
        agent_interface = 'Agent/1234'
        agent_id = 6
        agents_config = Mock()
        agents_config.keeplist = {
            str(agent_id): {
                'number': agent_number,
            }
        }
        self.innerdata.xod_config = {
            'agents': agents_config
        }

        result = self.agent_dao.get_id_from_interface(agent_interface)

        self.assertEqual(result, agent_id)

    def test_get_id_from_interface_not_an_agent(self):
        agent_interface = 'SIP/abcdef'

        self.assertRaises(ValueError, self.agent_dao.get_id_from_interface, agent_interface)

    def test_get_id_from_number(self):
        agent_number = '1234'
        agent_id = 6
        agents_config = Mock()
        agents_config.keeplist = {
            str(agent_id): {
                'number': agent_number,
            }
        }
        self.innerdata.xod_config = {
            'agents': agents_config
        }

        result = self.agent_dao.get_id_from_number(agent_number)

        self.assertEqual(result, agent_id)

    def test_is_completely_paused_yes(self):
        expected_result = True
        agent_id = 12
        self.queue_member_manager.get_paused_count_by_member_name.return_value = 2
        self.queue_member_manager.get_queue_count_by_member_name.return_value = 2
        self.agent_dao.get_interface_from_id = Mock(return_value='Agent/1234')

        result = self.agent_dao.is_completely_paused(agent_id)

        self.assertEqual(result, expected_result)

    def test_is_completely_paused_no(self):
        expected_result = False
        agent_id = 12
        self.queue_member_manager.get_paused_count_by_member_name.return_value = 1
        self.queue_member_manager.get_queue_count_by_member_name.return_value = 2
        self.agent_dao.get_interface_from_id = Mock(return_value='Agent/1234')

        result = self.agent_dao.is_completely_paused(agent_id)

        self.assertEqual(result, expected_result)

    def test_is_completely_paused_no_queues(self):
        expected_result = False
        agent_id = 12
        self.queue_member_manager.get_paused_count_by_member_name.return_value = 0
        self.queue_member_manager.get_queue_count_by_member_name.return_value = 0
        self.agent_dao.get_interface_from_id = Mock(return_value='Agent/1234')

        result = self.agent_dao.is_completely_paused(agent_id)

        self.assertEqual(result, expected_result)

    def test_get_interface_from_id(self):
        agent_id = 12
        agent_number = '1234'
        expected_interface = 'Agent/1234'

        agent_configs = Mock()
        agent_configs.keeplist = {str(agent_id): {'number': agent_number}}
        self.innerdata.xod_config = {'agents': agent_configs}

        result = self.agent_dao.get_interface_from_id(agent_id)

        self.assertEqual(result, expected_interface)

    def test_is_logged(self):
        agent_id = 12

        agent_status = {str(agent_id): {'availability': AgentStatus.logged_out}}
        self.innerdata.xod_status = {'agents': agent_status}

        result = self.agent_dao.is_logged(agent_id)

        self.assertEqual(result, False)

    def test_is_logged_true(self):
        agent_id = 12

        agent_status = {str(agent_id): {'availability': AgentStatus.available}}
        self.innerdata.xod_status = {'agents': agent_status}

        result = self.agent_dao.is_logged(agent_id)

        self.assertEqual(result, True)

    def test_set_on_call_acd(self):
        agent_id = 12
        self.innerdata.xod_status = {
            'agents': {
                str(agent_id): {
                    'on_call_acd': False
                }
            }
        }

        self.agent_dao.set_on_call_acd(agent_id, True)

        self.assertTrue(self.innerdata.xod_status['agents'][str(agent_id)]['on_call_acd'])

    def test_on_call_acd(self):
        agent_id = 12
        self.innerdata.xod_status = {
            'agents': {
                str(agent_id): {
                    'on_call_acd': True
                }
            }
        }
        expected_result = True

        result = self.agent_dao.on_call_acd(agent_id)

        self.assertEqual(result, expected_result)

    def test_set_on_call_nonacd(self):
        agent_id = 12
        self.innerdata.xod_status = {
            'agents': {
                str(agent_id): {
                    'on_call_nonacd': False
                }
            }
        }

        self.agent_dao.set_on_call_nonacd(agent_id, True)

        self.assertTrue(self.innerdata.xod_status['agents'][str(agent_id)]['on_call_nonacd'])

    def test_on_call_nonacd(self):
        agent_id = 12
        self.innerdata.xod_status = {
            'agents': {
                str(agent_id): {
                    'on_call_nonacd': True
                }
            }
        }
        expected_result = True

        result = self.agent_dao.on_call_nonacd(agent_id)

        self.assertEqual(result, expected_result)

    def test_set_on_wrapup(self):
        agent_id = 12
        self.innerdata.xod_status = {
            'agents': {
                str(agent_id): {
                    'on_wrapup': False
                }
            }
        }

        self.agent_dao.set_on_wrapup(agent_id, True)

        self.assertTrue(self.innerdata.xod_status['agents'][str(agent_id)]['on_wrapup'])

    def test_on_wrapup(self):
        agent_id = 12
        self.innerdata.xod_status = {
            'agents': {
                str(agent_id): {
                    'on_wrapup': True
                }
            }
        }

        result = self.agent_dao.on_wrapup(agent_id)

        self.assertTrue(result, True)

    def test_add_to_queue(self):
        queue_id = 13
        agent_id = 42
        self.innerdata.xod_status = {
            'agents': {
                str(agent_id): {
                    'queues': [
                        "3"
                    ]
                }
            }
        }

        self.agent_dao.add_to_queue(agent_id, queue_id)

        self.assertTrue(str(queue_id) in self.innerdata.xod_status['agents'][str(agent_id)]['queues'])

    def test_add_to_queue_already_added(self):
        queue_id = 13
        agent_id = 42
        self.innerdata.xod_status = {
            'agents': {
                str(agent_id): {
                    'queues': [
                        "3",
                        "13"
                    ]
                }
            }
        }
        expected_result = ["3", "13"]

        self.agent_dao.add_to_queue(agent_id, queue_id)

        self.assertEqual(expected_result, self.innerdata.xod_status['agents'][str(agent_id)]['queues'])

    def test_remove_from_queue(self):
        queue_id = 13
        agent_id = 42

        self.innerdata.xod_status = {
            'agents': {
                str(agent_id): {
                    'queues': [
                        "3",
                        str(queue_id)
                    ]
                }
            }
        }

        self.agent_dao.remove_from_queue(agent_id, queue_id)

        self.assertFalse(str(queue_id) in self.innerdata.xod_status['agents'][str(agent_id)]['queues'])

    def test_remove_from_queue_already_removed(self):
        queue_id = 13
        agent_id = 42

        self.innerdata.xod_status = {
            'agents': {
                str(agent_id): {
                    'queues': [
                        "3",
                    ]
                }
            }
        }

        self.agent_dao.remove_from_queue(agent_id, queue_id)

        self.assertFalse(str(queue_id) in self.innerdata.xod_status['agents'][str(agent_id)]['queues'])
