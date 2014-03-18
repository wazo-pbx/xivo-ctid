# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

import base64
import logging
import threading
import urllib
import urllib2

from xivo_cti.services.device.controller import base

logger = logging.getLogger(__name__)


class SnomController(base.BaseController):

    _username, _password = 'guest', 'guest'

    def answer(self, device):
        answerer = self._get_answerer(device.ip, self._username, self._password)
        threading.Thread(target=answerer.answer).start()

    def _get_answerer(self, hostname, username, password):
        return _SnomAnswerer(hostname, username, password)


class _SnomAnswerer(object):

    _auth_string = u'%(username)s:%(password)s'
    _command_url = u'http://%(hostname)s/command.htm'
    _data = {'key': 'P1'}

    def __init__(self, hostname, username, password):
        self._hostname = hostname
        self._username = username
        self._password = password

    def __eq__(self, other):
        return ((self._hostname, self._username, self._password) ==
                (other._hostname, other._username, other._password))

    def answer(self):
        req = self._get_request()
        try:
            urllib2.urlopen(req)
        except urllib2.URLError:
            logger.error('Failed to answer device %s', self._hostname)

    def _encoded_auth(self):
        auth_params = {
            'username': self._username,
            'password': self._password,
        }
        return base64.standard_b64encode(self._auth_string % auth_params)

    def _get_url_string(self):
        url_params = {'hostname': self._hostname}
        return self._command_url % url_params

    def _get_headers(self):
        auth_header = 'Basic %s' % self._encoded_auth()
        return {'Authorization': auth_header}

    def _get_data(self):
        return urllib.urlencode(self._data)

    def _get_request(self):
        return urllib2.Request(
            self._get_url_string(),
            self._get_data(),
            self._get_headers(),
        )
