# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, call, patch
from xivo_cti import innerdata
from xivo_cti.dao.agent_dao import notify_clients, AgentDAO, AgentCallStatus
from xivo_cti.exception import NoSuchAgentException
from xivo_cti.services.queue_member.manager import QueueMemberManager
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.services.call.direction import CallDirection

AGENT_ID = 12


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

        self.assertEqual(d.count, 1)
        self.assertEqual(d.agent_id, agent_id)
        expected = [call('setforce', ('agents', 'updatestatus', agent_id)), call('empty_stack')]
        arg_list = self.innerdata.handle_cti_stack.call_args_list
        self.assertEqual(arg_list, expected)


class TestAgentDAO(unittest.TestCase):

    def setUp(self):
        self.innerdata = Mock(innerdata.Safe)
        self.queue_member_manager = Mock(QueueMemberManager)
        self.agent_dao = AgentDAO(self.innerdata, self.queue_member_manager)

    def test_get_id_from_interface(self):
        agent_number = '1234'
        agent_interface = 'Agent/1234'
        agents_config = Mock()
        agents_config.keeplist = {
            str(AGENT_ID): {
                'number': agent_number,
            }
        }
        self.innerdata.xod_config = {
            'agents': agents_config
        }

        result = self.agent_dao.get_id_from_interface(agent_interface)

        self.assertEqual(result, AGENT_ID)

    def test_get_id_from_interface_not_an_agent(self):
        agent_interface = 'SIP/abcdef'

        self.assertRaises(ValueError, self.agent_dao.get_id_from_interface, agent_interface)

    def test_get_id_from_number(self):
        agent_number = '1234'
        agents_config = Mock()
        agents_config.keeplist = {
            str(AGENT_ID): {
                'number': agent_number,
            }
        }
        self.innerdata.xod_config = {
            'agents': agents_config
        }

        result = self.agent_dao.get_id_from_number(agent_number)

        self.assertEqual(result, AGENT_ID)

    def test_get_interface_from_id(self):
        agent_number = '1234'
        expected_interface = 'Agent/1234'

        agent_configs = Mock()
        agent_configs.keeplist = {str(AGENT_ID): {'number': agent_number}}
        self.innerdata.xod_config = {'agents': agent_configs}

        result = self.agent_dao.get_interface_from_id(AGENT_ID)

        self.assertEqual(result, expected_interface)

    @patch('time.time')
    def test_set_agent_status(self, mock_time):
        time_now = 123456789
        mock_time.return_value = time_now
        expected_agent_availability = AgentStatus.available
        expected_agent_availability_since = time_now
        self.innerdata.xod_status = {
            'agents': {
                str(AGENT_ID): {
                    'availability': AgentStatus.logged_out,
                    'availability_since': time_now - 300,
                }
            }
        }

        self.agent_dao.set_agent_availability(AGENT_ID, expected_agent_availability)

        agent_status = self.innerdata.xod_status['agents'][str(AGENT_ID)]

        self.assertEqual(expected_agent_availability, agent_status['availability'])
        self.assertEqual(expected_agent_availability_since, agent_status['availability_since'])

    @patch('time.time')
    def test_set_agent_status_no_cti_state_change(self, mock_time):
        time_now = 123456789
        mock_time.return_value = time_now
        expected_agent_availability = AgentStatus.unavailable
        expected_agent_availability_since = time_now - 400
        self.innerdata.xod_status = {
            'agents': {
                str(AGENT_ID): {
                    'availability': AgentStatus.unavailable,
                    'availability_since': expected_agent_availability_since,
                }
            }
        }

        self.agent_dao.set_agent_availability(AGENT_ID, expected_agent_availability)

        agent = self.innerdata.xod_status['agents'][str(AGENT_ID)]

        self.assertEqual(expected_agent_availability, agent['availability'])
        self.assertEqual(expected_agent_availability_since, agent['availability_since'])

    def test_set_agent_availability_on_a_removed_agent(self):
        agent_availability = AgentStatus.unavailable
        self.innerdata.xod_status = {
            'agents': {}
        }
        self.assertRaises(NoSuchAgentException, self.agent_dao.set_agent_availability, AGENT_ID, agent_availability)

    def test_agent_status(self):
        expected_status = {
            'availability': AgentStatus.logged_out,
            'availability_since': 1234566778,
            'channel': 'Agent/4242',
        }
        self.innerdata.xod_status = {
            'agents': {
                str(AGENT_ID): {
                    'availability': AgentStatus.logged_out,
                    'availability_since': 1234566778,
                    'channel': 'Agent/4242',
                }
            }
        }

        agent_status = self.agent_dao.agent_status(AGENT_ID)

        self.assertEqual(agent_status, expected_status)

    def test_is_completely_paused_yes(self):
        expected_result = True
        self.queue_member_manager.get_paused_count_by_member_name.return_value = 2
        self.queue_member_manager.get_queue_count_by_member_name.return_value = 2
        self.agent_dao.get_interface_from_id = Mock(return_value='Agent/1234')

        result = self.agent_dao.is_completely_paused(AGENT_ID)

        self.assertEqual(result, expected_result)

    def test_is_completely_paused_no(self):
        expected_result = False
        self.queue_member_manager.get_paused_count_by_member_name.return_value = 1
        self.queue_member_manager.get_queue_count_by_member_name.return_value = 2
        self.agent_dao.get_interface_from_id = Mock(return_value='Agent/1234')

        result = self.agent_dao.is_completely_paused(AGENT_ID)

        self.assertEqual(result, expected_result)

    def test_is_completely_paused_no_queues(self):
        expected_result = False
        self.queue_member_manager.get_paused_count_by_member_name.return_value = 0
        self.queue_member_manager.get_queue_count_by_member_name.return_value = 0
        self.agent_dao.get_interface_from_id = Mock(return_value='Agent/1234')

        result = self.agent_dao.is_completely_paused(AGENT_ID)

        self.assertEqual(result, expected_result)

    def test_set_on_call_acd(self):
        self.innerdata.xod_status = {
            'agents': {
                str(AGENT_ID): {
                    'on_call_acd': False
                }
            }
        }

        self.agent_dao.set_on_call_acd(AGENT_ID, True)

        self.assertTrue(self.innerdata.xod_status['agents'][str(AGENT_ID)]['on_call_acd'])

    def test_on_call_acd(self):
        self.innerdata.xod_status = {
            'agents': {
                str(AGENT_ID): {
                    'on_call_acd': True
                }
            }
        }
        expected_result = True

        result = self.agent_dao.on_call_acd(AGENT_ID)

        self.assertEqual(result, expected_result)

    def test_set_on_wrapup(self):
        self.innerdata.xod_status = {
            'agents': {
                str(AGENT_ID): {
                    'on_wrapup': False
                }
            }
        }

        self.agent_dao.set_on_wrapup(AGENT_ID, True)

        self.assertTrue(self.innerdata.xod_status['agents'][str(AGENT_ID)]['on_wrapup'])

    def test_on_wrapup(self):
        self.innerdata.xod_status = {
            'agents': {
                str(AGENT_ID): {
                    'on_wrapup': True
                }
            }
        }

        result = self.agent_dao.on_wrapup(AGENT_ID)

        self.assertTrue(result, True)

    def test_add_to_queue(self):
        queue_id = 13
        self.innerdata.xod_status = {
            'agents': {
                str(AGENT_ID): {
                    'queues': [
                        "3"
                    ]
                }
            }
        }

        self.agent_dao.add_to_queue(AGENT_ID, queue_id)

        self.assertTrue(str(queue_id) in self.innerdata.xod_status['agents'][str(AGENT_ID)]['queues'])

    def test_add_to_queue_already_added(self):
        queue_id = 13
        self.innerdata.xod_status = {
            'agents': {
                str(AGENT_ID): {
                    'queues': [
                        "3",
                        "13"
                    ]
                }
            }
        }
        expected_result = ["3", "13"]

        self.agent_dao.add_to_queue(AGENT_ID, queue_id)

        self.assertEqual(expected_result, self.innerdata.xod_status['agents'][str(AGENT_ID)]['queues'])

    def test_remove_from_queue(self):
        queue_id = 13

        self.innerdata.xod_status = {
            'agents': {
                str(AGENT_ID): {
                    'queues': [
                        "3",
                        str(queue_id)
                    ]
                }
            }
        }

        self.agent_dao.remove_from_queue(AGENT_ID, queue_id)

        self.assertFalse(str(queue_id) in self.innerdata.xod_status['agents'][str(AGENT_ID)]['queues'])

    def test_remove_from_queue_already_removed(self):
        queue_id = 13

        self.innerdata.xod_status = {
            'agents': {
                str(AGENT_ID): {
                    'queues': [
                        "3",
                    ]
                }
            }
        }

        self.agent_dao.remove_from_queue(AGENT_ID, queue_id)

        self.assertFalse(str(queue_id) in self.innerdata.xod_status['agents'][str(AGENT_ID)]['queues'])

    def test_set_nonacd_call_status(self):
        self.innerdata.xod_status = {
            'agents': {
                str(AGENT_ID): {
                }
            }
        }
        call_status = AgentCallStatus(direction=CallDirection.incoming,
                                      is_internal=False)

        self.agent_dao.set_nonacd_call_status(AGENT_ID, call_status)

        result = self.innerdata.xod_status['agents'][str(AGENT_ID)]['nonacd_call_status']

        self.assertEquals(call_status, result)

    def test_on_call_nonacd(self):
        self.innerdata.xod_status = {
            'agents': {
                str(AGENT_ID): {
                }
            }
        }
        call_status = AgentCallStatus(direction=CallDirection.incoming,
                                      is_internal=False)

        self.agent_dao.set_nonacd_call_status(AGENT_ID, call_status)
        result = self.agent_dao.on_call_nonacd(AGENT_ID)
        self.assertEquals(result, True)

        self.agent_dao.set_nonacd_call_status(AGENT_ID, None)
        result = self.agent_dao.on_call_nonacd(AGENT_ID)
        self.assertEquals(result, False)

    def test_nonacd_call_status(self):
        call_status = AgentCallStatus(direction=CallDirection.incoming,
                                      is_internal=False)
        expected_result = call_status
        self.innerdata.xod_status = {
            'agents': {
                str(AGENT_ID): {
                    'nonacd_call_status': call_status,
                }
            }
        }

        result = self.agent_dao.nonacd_call_status(AGENT_ID)

        self.assertEquals(expected_result, result)
