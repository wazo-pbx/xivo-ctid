# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
