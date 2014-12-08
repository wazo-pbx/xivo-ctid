# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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
from xivo_cti.lists.queues_list import QueuesList


class TestQueuesList(unittest.TestCase):

    def setUp(self):
        innerdata = Mock()
        self.queues_list = QueuesList(innerdata)

    def test_idbyqueuename(self):
        queue_id = 1
        queue_name = 'foo'
        self._set_keeplist({
            str(queue_id): {
                'id': queue_id,
                'name': queue_name,
            }
        })

        result = self.queues_list.idbyqueuename(queue_name)

        self.assertEqual(result, str(queue_id))

    def test_idbyqueuename_not_found(self):
        self._set_keeplist({})

        result = self.queues_list.idbyqueuename('foo')

        self.assertTrue(result is None)

    def test_get_queue_by_name(self):
        queue_id = 1
        queue_name = 'foo'
        queue = {
            'id': queue_id,
            'name': queue_name,
        }
        self._set_keeplist({str(queue_id): queue})

        result = self.queues_list.get_queue_by_name(queue_name)

        self.assertEqual(result, queue)

    def test_get_queue_by_name_not_found(self):
        self._set_keeplist({})

        result = self.queues_list.get_queue_by_name('foo')

        self.assertTrue(result is None)

    def _set_keeplist(self, keeplist):
        self.queues_list.keeplist = keeplist
        self.queues_list._init_reverse_dictionary()
