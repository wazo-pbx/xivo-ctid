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
from mock import Mock, sentinel
from xivo_cti.task_scheduler import _TaskScheduler


class TestTaskScheduler(unittest.TestCase):

    def setUp(self):
        self.time_function = Mock()
        self.task_scheduler = _TaskScheduler(self.time_function)

    def test_schedule_and_run_due_task(self):
        self.time_function.side_effect = [0.0, 3.0]
        function = Mock()

        self.task_scheduler.schedule(2.0, function, sentinel.args1)
        self.task_scheduler.run()

        function.assert_called_once_with(sentinel.args1)

    def test_schedule_and_dont_run_undue_task(self):
        self.time_function.side_effect = [0.0, 1.0]
        function = Mock()

        self.task_scheduler.schedule(2.0, function)
        self.task_scheduler.run()

        self.assertFalse(function.called)

    def test_schedule_and_run_only_once(self):
        self.time_function.side_effect = [0.0, 2.0, 3.0]
        function = Mock()

        self.task_scheduler.schedule(1.0, function)
        self.task_scheduler.run()
        self.task_scheduler.run()

        function.assert_called_once_with()

    def test_timeout_no_task(self):
        timeout = self.task_scheduler.timeout()

        self.assertTrue(timeout is None)

    def test_timeout_due_task(self):
        self.time_function.side_effect = [0.0, 1.0]
        self.task_scheduler.schedule(0.5, Mock())

        timeout = self.task_scheduler.timeout()

        self.assertEqual(timeout, 0.0)

    def test_timeout_undue_task(self):
        self.time_function.side_effect = [0.0, 1.0]
        self.task_scheduler.schedule(1.5, Mock())

        timeout = self.task_scheduler.timeout()

        self.assertEqual(timeout, 0.5)

    def test_cancel_then_timeout(self):
        self.time_function.side_effect = [0.0, 0.0]
        function = Mock()

        task = self.task_scheduler.schedule(1.0, function)
        task.cancel()
        timeout = self.task_scheduler.timeout()

        self.assertTrue(timeout is None)

    def test_cancel_then_run(self):
        self.time_function.side_effect = [0.0, 0.0, 2.0]
        function1 = Mock()
        function2 = Mock()

        self.task_scheduler.schedule(1.0, function1)
        self.task_scheduler.schedule(1.0, function2).cancel()
        self.task_scheduler.run()

        function1.assert_called_once_with()
        self.assertFalse(function2.called)

    def test_cancel_multiple_time_doesnt_raise(self):
        self.time_function.side_effect = [0.0]
        function = Mock()

        task = self.task_scheduler.schedule(1.0, function)
        task.cancel()
        task.cancel()

    def test_clear(self):
        self.time_function.side_effect = [0.0, 1.0]
        function = Mock()

        self.task_scheduler.schedule(0.0, function)
        self.task_scheduler.clear()
        self.task_scheduler.run()

        self.assertFalse(function.called)
