# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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


logger = logging.getLogger(__name__)


class AsyncRunner(object):

    def __init__(self, thread_pool_executor, task_queue):
        self._thread_pool_executor = thread_pool_executor
        self._task_queue = task_queue

    def run(self, function, *args, **kwargs):
        self._thread_pool_executor.submit(self._exec, function, *args, **kwargs)

    def run_with_cb(self, cb, function, *args, **kwargs):
        self._thread_pool_executor.submit(self._exec_with_cb, cb, function, *args, **kwargs)

    def stop(self):
        self._thread_pool_executor.shutdown(wait=True)
        self._task_queue.run()

    def _exec(self, function, *args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception:
            logger.exception('Exception in async function %s', function)

    def _exec_with_cb(self, cb, function, *args, **kwargs):
        result = self._exec(function, *args, **kwargs)
        self._task_queue.put(cb, result)
