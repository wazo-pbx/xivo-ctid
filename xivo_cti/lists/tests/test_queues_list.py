# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock
from xivo_cti.lists.queues_list import QueuesList


class TestQueuesList(unittest.TestCase):

    def setUp(self):
        innerdata = Mock()
        self.queues_list = QueuesList(innerdata)

    def test_queues_by_name_after_init(self):
        queue_id = '6'
        queue_name = 'foo'
        queue = {'name': queue_name}
        self.queues_list.keeplist = {
            queue_id: queue,
        }

        self.queues_list._init_reverse_dictionary()

        self.assertEqual(self.queues_list.queues_by_name, {queue_name: queue})

    def _set_keeplist(self, keeplist):
        self.queues_list.keeplist = keeplist
        self.queues_list._init_reverse_dictionary()
