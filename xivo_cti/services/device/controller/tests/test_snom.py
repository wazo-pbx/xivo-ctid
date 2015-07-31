# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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

import unittest

from hamcrest import assert_that
from hamcrest import equal_to
from mock import patch
from mock import ANY
from xivo_cti.model.device import Device
from xivo_cti.services.device.controller.snom import SnomController, _SnomAnswerer


class TestSnomController(unittest.TestCase):

    def setUp(self):
        self.username = 'foo'
        self.password = 'bar'
        self.answer_delay = 0.1
        self.device = Device(2)
        self.device.ip = '127.0.0.1'
        self.controller = SnomController(self.username, self.password, self.answer_delay)

    def test_new_answerer(self):
        answerer = self.controller._new_answerer(self.device)

        self.assertIsInstance(answerer, _SnomAnswerer)

    def test_new_from_config(self):
        config = {
            'switchboard_snom': {
                'username': self.username,
                'password': self.password,
                'answer_delay': str(self.answer_delay),
            }
        }

        with patch('xivo_cti.services.device.controller.snom.config', config):
            controller = SnomController.new_from_config()

        assert_that(controller._username, equal_to(self.username))
        assert_that(controller._password, equal_to(self.password))
        assert_that(controller._answer_delay, equal_to(self.answer_delay))


class TestSnomAnswerer(unittest.TestCase):

    def setUp(self):
        self.hostname = '127.0.0.1'
        self.username = 'foo'
        self.password = 'bar'
        self.answerer = _SnomAnswerer(self.hostname, self.username, self.password)

    @patch('xivo_cti.services.device.controller.snom.requests')
    def test_answer(self, mock_requests):
        expected_url = 'http://{hostname}/command.htm?key=P1'.format(hostname=self.hostname)
        expected_timeout = self.answerer._TIMEOUT

        self.answerer.answer()

        mock_requests.get.assert_called_once_with(expected_url,
                                                  auth=ANY,
                                                  timeout=expected_timeout)
