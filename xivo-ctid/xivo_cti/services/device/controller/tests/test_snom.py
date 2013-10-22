# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

import time
import unittest
import urllib2

from base64 import standard_b64encode
from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import less_than
from mock import Mock
from mock import patch
from mock import sentinel
from xivo_cti.services.device.controller.snom import SnomController
from xivo_cti.services.device.controller.snom import _SnomAnswerer
from xivo_dao.data_handler.device.model import Device


class TestSnomController(unittest.TestCase):

    def setUp(self):
        self._ami_class = None

    def test_answer(self):
        device = Device(ip='127.0.0.1')
        snom_controller = SnomController(self._ami_class)
        answerer = Mock(_SnomAnswerer)
        snom_controller._get_answerer = Mock(return_value=answerer)

        snom_controller.answer(device)

        snom_controller._get_answerer.assert_called_once_with(device.ip, 'guest', 'guest')
        answerer.answer.assert_called_once_with()

    def test_answer_blocking(self):
        device = Device(ip='127.0.0.1')
        snom_controller = SnomController(self._ami_class)
        answerer = Mock(_SnomAnswerer)
        snom_controller._get_answerer = Mock(return_value=answerer)
        answerer.answer.side_effect = lambda: time.sleep(0.2)

        call_time = time.time()
        snom_controller.answer(device)
        return_time = time.time()

        elapsed_time = return_time - call_time
        assert_that(elapsed_time, less_than(0.1), 'Time spent in a blocking answer in second')

    def test_get_answerer(self):
        ip = '127.0.0.1'
        username = 'guest'
        password = 'secret'

        snom_controller = SnomController(self._ami_class)
        answerer = snom_controller._get_answerer(ip, username, password)

        expected_answerer = _SnomAnswerer(ip, username, password)
        assert_that(answerer, equal_to(expected_answerer))


class TestSnomAnswerer(unittest.TestCase):

    def setUp(self):
        self._username = 'guest'
        self._password = 'pword'
        self._ip = '127.0.0.1'

        self._answerer = _SnomAnswerer(self._ip, self._username, self._password)

    @patch('urllib2.urlopen')
    def test_answer(self, mock_urlopen):
        req = sentinel
        self._answerer._get_request = Mock(return_value=req)

        self._answerer.answer()

        mock_urlopen.assert_called_once_with(req)

    @patch('urllib2.urlopen', Mock(side_effect=urllib2.URLError('unexpected error')))
    def test_answer_error_does_not_raise(self):
        self._answerer._get_request = Mock(return_value=None)

        self._answerer.answer()

    def test_snom_answerer_auth(self):
        encoded_auth = self._answerer._encoded_auth()

        assert_that(encoded_auth, equal_to(self._encoded_auth()))

    def test_get_url_string(self):
        url = self._answerer._get_url_string()

        expected_url = 'http://%s/command.htm' % self._ip
        assert_that(url, equal_to(expected_url))

    def test_get_headers(self):
        headers = self._answerer._get_headers()

        expected_headers = {'Authorization': 'Basic %s' % self._encoded_auth()}
        assert_that(headers, equal_to(expected_headers))

    def test_get_data(self):
        data = self._answerer._get_data()

        expected_data = 'key=P1'
        assert_that(data, equal_to(expected_data))

    def test_get_request(self):
        url = 'http://example.com'
        data = {'fruit': 'apple'}
        headers = {}
        self._answerer._get_data = Mock(return_value=data)
        self._answerer._get_headers = Mock(return_value=headers)
        self._answerer._get_url_string = Mock(return_value=url)

        req = self._answerer._get_request()

        expected_request = urllib2.Request(url, data, headers)
        assert_that(req.get_host(), equal_to(expected_request.get_host()))
        assert_that(req.get_data(), equal_to(expected_request.get_data()))
        assert_that(req.headers, equal_to(expected_request.headers))

    def _encoded_auth(self):
        return standard_b64encode('%s:%s' % (self._username, self._password))
