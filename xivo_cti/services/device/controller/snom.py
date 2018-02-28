# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging
import os
import requests

from xivo_cti import config
from xivo_cti.services.device.controller.async import AsyncController
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class SnomController(AsyncController):

    def __init__(self, username, password, answer_delay):
        super(SnomController, self).__init__(answer_delay)
        self._username = username
        self._password = password

    def _new_answerer(self, device):
        return _SnomAnswerer(device.ip, self._username, self._password)

    @classmethod
    def new_from_config(cls):
        username = config['switchboard_snom']['username']
        password = config['switchboard_snom']['password']
        env_answer_delay = os.getenv('SNOM_SB_ANSWER_DELAY')
        if env_answer_delay is None:
            answer_delay = float(config['switchboard_snom']['answer_delay'])
        else:
            answer_delay = float(env_answer_delay)
        return cls(username, password, answer_delay)


class _SnomAnswerer(object):

    _TIMEOUT = 5

    def __init__(self, hostname, username, password):
        self._hostname = hostname
        self._username = username
        self._password = password

    def answer(self):
        url = 'http://{hostname}/command.htm?key=P1'.format(hostname=self._hostname)
        auth = HTTPBasicAuth(self._username, self._password)
        try:
            r = requests.get(url, auth=auth, timeout=self._TIMEOUT)
        except requests.RequestException:
            logger.exception('Failed to answer %s: unexpected error', self._hostname)
        else:
            if r.status_code != 200:
                logger.error('Failed to answer %s: HTTP status code %s', self._hostname, r.status_code)
