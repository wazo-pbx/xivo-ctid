# -*- coding: utf-8 -*-

# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
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
import requests

from xivo_cti import config
from xivo_cti.services.device.controller.async import AsyncController
from requests.auth import HTTPDigestAuth

logger = logging.getLogger(__name__)


class PolycomController(AsyncController):

    def __init__(self, username, password, answer_delay):
        super(PolycomController, self).__init__(answer_delay)
        self._username = username
        self._password = password

    def _new_answerer(self, device):
        return _PolycomAnswerer(device.ip, self._username, self._password)

    @classmethod
    def new_from_config(cls):
        username = config['switchboard_polycom']['username']
        password = config['switchboard_polycom']['password']
        answer_delay = float(config['switchboard_polycom']['answer_delay'])
        return cls(username, password, answer_delay)


class _PolycomAnswerer(object):

    _HEADERS = {
        'Content-Type': 'application/x-com-polycom-spipx',
    }
    _DATA = '<PolycomIPPhone><Data priority="Important">Key:Line1</Data></PolycomIPPhone>'
    _TIMEOUT = 5

    def __init__(self, hostname, username, password):
        self._hostname = hostname
        self._username = username
        self._password = password

    def answer(self):
        url = 'http://{hostname}/push'.format(hostname=self._hostname)
        auth = HTTPDigestAuth(self._username, self._password)
        try:
            r = requests.post(url,
                              headers=self._HEADERS,
                              data=self._DATA,
                              auth=auth,
                              timeout=self._TIMEOUT)
        except requests.RequestException:
            logger.exception('Failed to answer %s: unexpected error', self._hostname)
        else:
            if r.status_code != 200:
                logger.error('Failed to answer %s: HTTP status code %s', self._hostname, r.status_code)
