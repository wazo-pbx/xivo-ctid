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

from mock import ANY
from mock import Mock
from mock import patch
from unittest import TestCase
from xivo_cti.scheduler import Scheduler

from ..dird import Dird


@patch('os.write', Mock())
class TestDird(TestCase):

    def setUp(self):
        self.scheduler = Scheduler()
        self.scheduler.setup(Mock())
        self.dird = Dird(self.scheduler)
        self.dird.executor = Mock()

    @patch('requests.get')
    def test_headers(self, http_get):
        callback = Mock()
        profile = 'my_profile'
        expected_url = 'http://localhost:50060/0.1/directories/lookup/{profile}/headers'.format(profile=profile)

        self.dird.headers(profile, callback)

        self.dird.executor.submit.assert_called_once_with(http_get, expected_url)
        self.dird.executor.submit.return_value.add_done_callback.assert_called_once_with(ANY)


def _unicode_list(binary_list):
    result = []
    for binary_element in binary_list:
        if binary_element:
            result.append(binary_element.decode('utf8'))
        else:  # may contain None
            result.append(binary_element)
    return result
