# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

from mock import Mock
from mock import patch
from xivo_cti.dao.innerdata_dao import InnerdataDAO
from xivo_cti.innerdata import Safe
from xivo_cti.exception import NotAQueueException


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

    @patch('xivo_cti.dao.innerdata_dao.config', {'profiles': {'client': {'userstatus': 2}},
                                                 'userstatus': {
                                                     2: {'available': {},
                                                         'disconnected': {}}}})
    def test_get_presences(self):
        profile = 'client'
        expected_result = ['available', 'disconnected']

        result = self.innerdata_dao.get_presences(profile)

        self.assertEquals(result, expected_result)

    def _assert_contains_same_elements(self, list, expected_list):
        self.assertEquals(len(list), len(expected_list))
        for element in list:
            self.assertTrue(element in expected_list)
