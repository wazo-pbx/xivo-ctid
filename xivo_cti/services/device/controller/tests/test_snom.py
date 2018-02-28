# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
