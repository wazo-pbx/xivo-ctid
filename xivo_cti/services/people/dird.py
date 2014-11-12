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

import json
import requests

from concurrent import futures


class Dird(object):

    _headers_url = 'http://localhost:50060/0.1/directories/lookup/{profile}/headers'

    def __init__(self, task_queue):
        self.executor = futures.ThreadPoolExecutor(max_workers=5)
        self._task_queue = task_queue

    def headers(self, profile, callback):
        def response_to_dict(f):
            self._task_queue.put(callback, json.loads(f.result().content))

        url = self._headers_url.format(profile=profile)
        future = self.executor.submit(requests.get, url)
        future.add_done_callback(response_to_dict)
