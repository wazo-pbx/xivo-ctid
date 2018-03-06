# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import select
import unittest
from mock import Mock, sentinel
from xivo_cti.task_queue import new_task_queue, _PollableQueue, _SignallableFileDescriptor


class TestTaskQueue(unittest.TestCase):

    def setUp(self):
        self.task_queue = new_task_queue()

    def tearDown(self):
        self.task_queue.close()

    def test_run(self):
        function = Mock()

        self.task_queue.put(function, sentinel.args1)
        self.task_queue.run()

        function.assert_called_once_with(sentinel.args1)


class TestPollableQueue(unittest.TestCase):

    def setUp(self):
        self.queue = _PollableQueue(_SignallableFileDescriptor())

    def tearDown(self):
        self.queue.close()

    def test_queue_get(self):
        self.queue.put(sentinel.item1)
        self.queue.put(sentinel.item2)

        self.assertEqual(self.queue.get_all(), [sentinel.item1, sentinel.item2])
        self.assertEqual(self.queue.get_all(), [])

    def test_file_descriptor_state(self):
        self.assertFalse(is_readable(self.queue))

        self.queue.put(sentinel.item1)

        self.assertTrue(is_readable(self.queue))

        self.queue.get_all()

        self.assertFalse(is_readable(self.queue))

    def test_signal_and_clear(self):
        signallable_fd = Mock()
        queue = _PollableQueue(signallable_fd)

        queue.put(sentinel.item1)
        queue.put(sentinel.item2)

        signallable_fd.signal.assert_called_once_with()

        queue.get_all()
        queue.get_all()

        signallable_fd.clear.assert_called_once_with()

    def test_close(self):
        signallable_fd = Mock()
        queue = _PollableQueue(signallable_fd)
        queue.close()

        signallable_fd.close.assert_called_once_with()


def is_readable(obj):
    r_rlist = select.select([obj], [], [], 0)[0]
    return bool(r_rlist)
