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
from mock import Mock, patch
from xivo_cti.dao.innerdata_dao import InnerdataDAO
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.innerdata import Safe
from xivo_cti.exception import NotAQueueException
from xivo_cti.exception import NoSuchAgentException


class TestInnerdataDAO(unittest.TestCase):

    def setUp(self):
        self.innerdata = Mock(Safe)
        self.innerdata_dao = InnerdataDAO(self.innerdata)

    def test_get_queue_id(self):
        expected_queue_id = '1'
        queue_name = 'services'
        self.innerdata_dao.get_queue_id = Mock()
        self.innerdata_dao.get_queue_id.return_value = '1'

        queue_id = self.innerdata_dao.get_queue_id(queue_name)

        self.assertEqual(queue_id, expected_queue_id)

    def test_get_queue_id_not_exist(self):
        queue_name = 'services'
        queues_config = Mock()
        queues_config.idbyqueuename = Mock()
        self.innerdata_dao.innerdata.xod_config = {'queues': queues_config}

        queues_config.idbyqueuename.side_effect = NotAQueueException()

        self.assertRaises(NotAQueueException,
                          self.innerdata_dao.get_queue_id,
                          queue_name)

    def test_get_queue_ids(self):
        inner_queue_list = Mock()
        inner_queue_list.get_queues.return_value = ['45', '77']
        self.innerdata_dao.innerdata.xod_config = {'queues': inner_queue_list}

        queue_ids = ['45', '77']

        returned_queue_ids = self.innerdata_dao.get_queue_ids()

        self._assert_contains_same_elements(returned_queue_ids, queue_ids)

        inner_queue_list.get_queues.assert_called_once_with()

    def test_get_presences(self):
        profile = 'client'
        expected_result = ['available', 'disconnected']
        get_config_return = {
            'profiles': {'client': {'userstatus': 2}},
            'userstatus': {
                2: {'available': {},
                    'disconnected': {}}
            }
        }
        self.innerdata_dao.innerdata._config = Mock()
        side_effect = lambda get_config_argument: get_config_return[get_config_argument]
        self.innerdata_dao.innerdata._config.getconfig.side_effect = side_effect

        result = self.innerdata_dao.get_presences(profile)

        self.assertEquals(result, expected_result)

    @patch('time.time')
    def test_set_agent_status(self, mock_time):
        time_now = 123456789
        mock_time.return_value = time_now
        expected_agent_availability = AgentStatus.available
        expected_agent_availability_since = time_now
        agent_id = 6573
        self.innerdata_dao.innerdata.xod_status = {
            'agents': {
                str(agent_id): {
                    'availability': AgentStatus.logged_out,
                    'availability_since': time_now - 300,
                }
            }
        }

        self.innerdata_dao.set_agent_availability(agent_id, expected_agent_availability)

        agent_status = self.innerdata_dao.innerdata.xod_status['agents'][str(agent_id)]

        self.assertEqual(expected_agent_availability, agent_status['availability'])
        self.assertEqual(expected_agent_availability_since, agent_status['availability_since'])

    @patch('time.time')
    def test_set_agent_status_no_cti_state_change(self, mock_time):
        time_now = 123456789
        mock_time.return_value = time_now
        expected_agent_availability = AgentStatus.unavailable
        expected_agent_availability_since = time_now - 400
        agent_id = 6573
        self.innerdata_dao.innerdata.xod_status = {
            'agents': {
                str(agent_id): {
                    'availability': AgentStatus.unavailable,
                    'availability_since': expected_agent_availability_since,
                }
            }
        }

        self.innerdata_dao.set_agent_availability(agent_id, expected_agent_availability)

        agent = self.innerdata_dao.innerdata.xod_status['agents'][str(agent_id)]

        self.assertEqual(expected_agent_availability, agent['availability'])
        self.assertEqual(expected_agent_availability_since, agent['availability_since'])

    def test_agent_status(self):
        agent_id = 42
        expected_status = {
            'availability': AgentStatus.logged_out,
            'availability_since': 1234566778,
            'channel': 'Agent/4242',
        }
        self.innerdata_dao.innerdata.xod_status = {
            'agents': {
                str(agent_id): {
                    'availability': AgentStatus.logged_out,
                    'availability_since': 1234566778,
                    'channel': 'Agent/4242',
                }
            }
        }

        agent_status = self.innerdata_dao.agent_status(agent_id)

        self.assertEqual(agent_status, expected_status)

    def test_set_agent_availability_on_a_removed_agent(self):
        agent_id = 42
        agent_availability = AgentStatus.unavailable
        self.innerdata_dao.innerdata.xod_status = {
            'agents': {}
        }
        self.assertRaises(NoSuchAgentException, self.innerdata_dao.set_agent_availability, agent_id, agent_availability)

    def _assert_contains_same_elements(self, list, expected_list):
        self.assertEquals(len(list), len(expected_list))
        for element in list:
            self.assertTrue(element in expected_list)
