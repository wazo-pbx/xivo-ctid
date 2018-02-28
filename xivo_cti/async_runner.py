# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from contextlib import contextmanager

logger = logging.getLogger(__name__)


@contextmanager
def synchronize(runner):
    yield
    runner._thread_pool_executor.shutdown(wait=True)
    runner._task_queue.run()


def async_runner_thread(f):
    """
    The decorated function is executed in the async runner's thread. This means
    that the implementation of the function should only manipulate it's
    parameters and call thread safe operations. Usually add a task to a task
    queue.

    The implementation of this decorator does nothing. It's just a warning for
    the next programmer reading the decorated function.
    """
    return f


class AsyncRunner(object):

    def __init__(self, thread_pool_executor, task_queue):
        self._thread_pool_executor = thread_pool_executor
        self._task_queue = task_queue

    def run(self, func, *args, **kwargs):
        callback = kwargs.pop('_on_response', None)
        error_callback = kwargs.pop('_on_error', None)
        self._thread_pool_executor.submit(self._exec_with_cb, callback, error_callback, func, *args, **kwargs)

    def run_with_cb(self, cb, func, *args, **kwargs):
        self.run(func, _on_response=cb, *args, **kwargs)

    def _exec_with_cb(self, cb, error_cb, func, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if cb:
                self._task_queue.put(cb, result)
        except Exception as e:
            if error_cb:
                self._task_queue.put(error_cb, e)
            else:
                logger.exception('Exception in async function %s', func)
