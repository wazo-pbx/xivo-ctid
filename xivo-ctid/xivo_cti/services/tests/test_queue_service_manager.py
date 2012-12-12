# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from tests.mock import Mock
from xivo_cti.services.queue_service_manager import QueueServiceManager
from xivo_cti.dao.innerdata_dao import InnerdataDAO
from xivo_cti.services.queue.exception import NotAQueueException


class TestQueueServiceManager(unittest.TestCase):

    def setUp(self):
        self.queue_service_manager = QueueServiceManager()
        self.queue_service_manager.dao.innerdata = Mock(InnerdataDAO)

    def tearDown(self):
        pass

    def test_get_queue_id(self):
        expected_queue_id = '1'
        queue_name = 'services'
        self.queue_service_manager.get_queue_id = Mock()
        self.queue_service_manager.get_queue_id.return_value = '1'

        queue_id = self.queue_service_manager.get_queue_id(queue_name)

        self.assertEqual(queue_id, expected_queue_id)

    def test_get_queue_id_not_exist(self):
        queue_name = 'services'
        self.queue_service_manager.get_queue_id = Mock()
        self.queue_service_manager.get_queue_id.side_effect = NotAQueueException('Not a queue!')

        self.assertRaises(NotAQueueException,
                          self.queue_service_manager.get_queue_id,
                          queue_name)

    def test_get_queue_ids(self):
        expected_result = ['12324', '65452']
        self.queue_service_manager.get_queue_ids = Mock()
        self.queue_service_manager.get_queue_ids.return_value = expected_result

        result = self.queue_service_manager.get_queue_ids()

        self.assertEquals(result, expected_result)
