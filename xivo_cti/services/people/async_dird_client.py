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

import logging

from concurrent import futures
from xivo_dird_client import Client

logger = logging.getLogger(__name__)


class AsyncDirdClient(object):

    def __init__(self, task_queue):
        self.executor = futures.ThreadPoolExecutor(max_workers=5)
        self._task_queue = task_queue
        self._client = self._new_client()

    def _new_client(self):
        return Client(host='localhost', port=9489, version='0.1')

    def headers(self, profile, callback):
        logger.debug('requesting directory headers on profile %s', profile)
        self.executor.submit(self._exec_async, callback, self._client.directories.headers, profile=profile)

    def lookup(self, profile, term, callback):
        logger.debug('requesting directory lookup for %s on profile %s', term, profile)
        self.executor.submit(self._exec_async, callback, self._client.directories.lookup, profile=profile, term=term)

    def _exec_async(self, response_callback, fn, *args, **kwargs):
        try:
            result = fn(*args, **kwargs)
        except Exception:
            logger.exception('Failed to query xivo-dird')
        else:
            self._task_queue.put(response_callback, result)
