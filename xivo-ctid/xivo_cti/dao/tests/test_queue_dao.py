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
# contracted with Avencall. See the LICENSE file at top of the source tree
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

from mock import Mock
from xivo_cti.dao.queue_dao import QueueDAO
from xivo_cti.lists.cti_queuelist import QueueList
from xivo_cti.innerdata import Safe
from xivo_cti.exception import NoSuchQueueException


class TestQueueDAO(unittest.TestCase):

    def setUp(self):
        self._innerdata = Mock(Safe)
        self._queuelist = Mock(QueueList)
        self._queuelist.keeplist = {}
        self._innerdata.xod_config = {
            'queues': self._queuelist
        }
        self.dao = QueueDAO(self._innerdata)

    def test__queue(self):
        queue_id = 206
        self._queuelist.keeplist[queue_id] = {
            'number': '3006',
            'context': 'ctx',
            'name': 'toto',
            'displayname': 'Call on hold',
        }

        result = self.dao._queue(queue_id)

        self.assertTrue(result, self._queuelist.keeplist[queue_id])

    def test__user_no_user(self):
        self.assertRaises(NoSuchQueueException, self.dao._queue, 206)

    def test_get_number_context_from_name(self):
        queue_number = '3001'
        queue_context = 'ctx'
        queue_name = '__switchboard'
        queue_id = 7
        queues_config = Mock()
        queues_config.keeplist = {
            '6': {
                'number': '3006',
                'context': 'ctx',
                'name': '__switchboard_hold',
                'displayname': 'Call on hold',
            },
            str(queue_id): {
                'number': queue_number,
                'context': queue_context,
                'name': queue_name,
                'displayname': 'Incoming calls',
            }
        }
        self.dao.innerdata.xod_config = {
            'queues': queues_config
        }

        result = self.dao.get_number_context_from_name(queue_name)
        expected = queue_number, queue_context

        self.assertEqual(result, expected)

    def test_get_number_context_from_name_no_result(self):
        queue_name = '__switchboard'
        queues_config = Mock()
        queues_config.keeplist = {
            '6': {
                'number': '3006',
                'context': 'ctx',
                'name': '__switchboard_hold',
                'displayname': 'Call on hold',
            },
        }
        self.dao.innerdata.xod_config = {
            'queues': queues_config
        }

        self.assertRaises(LookupError, self.dao.get_number_context_from_name, queue_name)

    def test_get_name_from_id(self):
        queue_id = '6'
        queue_name = 'test_name_queue'
        self._queuelist.keeplist[queue_id] = {
            'number': '3006',
            'context': 'ctx',
            'name': queue_name,
            'displayname': 'Call on hold',
        }
        result = self.dao.get_name_from_id(queue_id)

        self.assertEqual(result, queue_name)

    def test_get_name_from_id_no_queue(self):
        queue_id = '6'

        result = self.dao.get_name_from_id(queue_id)

        self.assertEqual(result, None)
