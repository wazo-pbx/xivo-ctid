# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from concurrent import futures
from hamcrest import assert_that, equal_to
from mock import Mock, patch, sentinel

from ..async_runner import AsyncRunner, synchronize
from xivo_cti.task_queue import new_task_queue


class TestAsyncRunner(unittest.TestCase):

    def setUp(self):
        self.thread_pool_executor = futures.ThreadPoolExecutor(max_workers=1)
        self.task_queue = new_task_queue()
        self.runner = AsyncRunner(self.thread_pool_executor, self.task_queue)

    def tearDown(self):
        self.task_queue.close()

    def test_run_no_callback(self):
        function = Mock()

        with synchronize(self.runner):
            self.runner.run(function, 'a', 42, test='lol')

        function.assert_called_once_with('a', 42, test='lol')

    def test_that_exceptions_are_logged_when_no_callback(self):
        function = Mock(side_effect=RuntimeError)

        with patch('xivo_cti.async_runner.logger') as logger:
            with synchronize(self.runner):
                self.runner.run(function)

            function.assert_called_once_with()
            assert_that(logger.exception.call_count, equal_to(1))

    def test_run_with_callback(self):
        function = Mock(return_value=sentinel.result)
        cb = Mock()

        with synchronize(self.runner):
            self.runner.run_with_cb(cb, function)

        cb.assert_called_once_with(sentinel.result)

    def test_run_with_callback_exception(self):
        function = Mock(side_effect=RuntimeError)
        cb = Mock()

        with synchronize(self.runner):
            self.runner.run_with_cb(cb, function)

        function.assert_called_once_with()
        self.assertFalse(cb.called)

    def test_run_with_on_response_param(self):
        callback = Mock()
        function = Mock()

        with synchronize(self.runner):
            self.runner.run(function, 'lol', 42, foo='bar', baz='foobar', _on_response=callback)

        function.assert_called_once_with('lol', 42, foo='bar', baz='foobar')
        callback.assert_called_once_with(function.return_value)

    def test_run_with_on_error_param(self):
        error_callback = Mock()
        error = RuntimeError('foo')
        function = Mock(side_effect=error)

        with synchronize(self.runner):
            self.runner.run(function, 'lol', 42, foo='bar', _on_error=error_callback)

        function.assert_called_once_with('lol', 42, foo='bar')
        error_callback.assert_called_once_with(error)
