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
