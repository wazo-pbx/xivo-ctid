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

import Queue

from xivo_cti import dao


class _Future(object):
    """
    Wrapper around a Queue.Queue to move return values and exceptions between
    threads. The get method of a future will raise an exception if an exception
    was raised in original thread
    """

    def __init__(self):
        self._queue = Queue.Queue()

    def put(self, response, error=None):
        self._queue.put((response, error))

    def get(self):
        response, error = self._queue.get()
        if error:
            raise error

        return response


class _Value(object):
    """
    A _Future when the value is known at creation time
    """

    def __init__(self, response):
        self._response = response

    def get(self):
        return self._response


class _AsyncCommandExecutor(object):

    def __init__(self, task_queue):
        self._task_queue = task_queue

    def __call__(self, f, *args, **kwargs):
        future = _Future()
        self._task_queue.put(self._put_result, future, f, *args, **kwargs)
        return future

    def _put_result(self, future, func, *args, **kwargs):
        try:
            result, error = func(*args, **kwargs), None
        except Exception as e:
            result, error = None, e

        future.put(result, error)


class MainThreadProxy(object):
    """
    All public methods (other than __init__) are run in the http server thread
    and should not use data from the main thread directly.

    All public methods must reture a _Future. Consumers will use .get() on the
    returned futures to retrieve the result or reraise the original exception.
    """

    def __init__(self, task_queue, xivo_uuid):
        self._exec = _AsyncCommandExecutor(task_queue)
        self._uuid = xivo_uuid

    def get_uuid(self):
        return _Value(self._uuid)

    def get_endpoint_status(self, endpoint_id):
        return self._exec(dao.phone.get_status, endpoint_id)

    def get_user_presence(self, user_id):
        return self._exec(dao.user.get_presence, user_id)

    def get_user(self, id_or_uuid):
        return self._exec(dao.user.get, id_or_uuid)
