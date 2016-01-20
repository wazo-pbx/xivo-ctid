# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
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

from hamcrest import assert_that, equal_to
from mock import Mock, patch

from ..service_discovery import self_check


class TestSelfCheck(unittest.TestCase):

    def setUp(self):
        self.http_port = 4242
        self.config = {'rest_api': {'http': {'port': self.http_port}}}

    @patch('xivo_cti.service_discovery.requests.get', return_value=Mock(status_code=404))
    def test_that_self_check_returns_false_if_infos_does_not_return_200(self, get):
        result = self_check(self.config)

        assert_that(result, equal_to(False))

        get.assert_called_once_with('http://localhost:4242/0.1/infos')

    @patch('xivo_cti.service_discovery.requests.get', return_value=Mock(status_code=200))
    def test_that_self_check_returns_true_if_infos_returns_200(self, get):
        result = self_check(self.config)

        assert_that(result, equal_to(True))

        get.assert_called_once_with('http://localhost:4242/0.1/infos')

    @patch('xivo_cti.service_discovery.requests.get', side_effect=Exception)
    def test_that_self_check_returns_false_on_exception(self, get):
        result = self_check(self.config)

        assert_that(result, equal_to(False))

        get.assert_called_once_with('http://localhost:4242/0.1/infos')
