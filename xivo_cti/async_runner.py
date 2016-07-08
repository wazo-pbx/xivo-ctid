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
