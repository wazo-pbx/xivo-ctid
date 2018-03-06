# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
import time

from mock import patch
from xivo_cti.services.queue_entry_manager import QueueEntry
from xivo_cti.services.queue_entry_encoder import QueueEntryEncoder


class TestQueueEntryEncoder(unittest.TestCase):

    _queue_name = 'test_queue'
    _queue_id = 2

    def setUp(self):
        self.now = time.time()
        self._queue_entries = {'111.11': QueueEntry(1, 'Tester One', '1111', self.now + 10, '111.11'),
                               '222.22': QueueEntry(2, 'Tester Two', '2222', self.now + 7, '222.22'),
                               '333.33': QueueEntry(3, 'Tester Three', '3333', self.now + 1, '333.33')}
        self._expected_queue_entry_list = [{'position': 1,
                                            'name': 'Tester One',
                                            'number': '1111',
                                            'join_time': self.now + 10,
                                            'uniqueid': '111.11'},
                                           {'position': 2,
                                            'name': 'Tester Two',
                                            'number': '2222',
                                            'join_time': self.now + 7,
                                            'uniqueid': '222.22'},
                                           {'position': 3,
                                            'name': 'Tester Three',
                                            'number': '3333',
                                            'join_time': self.now + 1,
                                            'uniqueid': '333.33'}]

    @patch('xivo_dao.queue_dao.id_from_name', return_value=_queue_id)
    def test_encode_queue_entry_update(self, mock_id_from_name):
        encoder = QueueEntryEncoder()

        expected = {'class': 'queueentryupdate',
                    'state': {'queue_name': self._queue_name,
                              'queue_id': self._queue_id,
                              'entries': self._expected_queue_entry_list}}

        result = encoder.encode(self._queue_name, self._queue_entries)

        self.assertEqual(result, expected)

    def test_encode_queue_entry(self):
        encoder = QueueEntryEncoder()
        q_entry = QueueEntry(1, 'Tester One', '1111', self.now + 10, '111.11')
        expected = {'position': 1,
                    'name': 'Tester One',
                    'number': '1111',
                    'join_time': self.now + 10,
                    'uniqueid': '111.11'}

        result = encoder._encode_queue_entry(q_entry)

        self.assertEqual(result, expected)

    def test_build_queue_entry_list(self):
        encoder = QueueEntryEncoder()

        result = encoder._build_entry_list(self._queue_entries)

        self.assertEqual(result, self._expected_queue_entry_list)

    @patch('xivo_dao.queue_dao.id_from_name', return_value=_queue_id)
    def test_build_state(self, mock_id_from_name):
        encoder = QueueEntryEncoder()

        expected = {'queue_name': self._queue_name,
                    'queue_id': self._queue_id,
                    'entries': self._expected_queue_entry_list}

        result = encoder._build_state(self._queue_name, self._expected_queue_entry_list)

        self.assertEqual(result, expected)
