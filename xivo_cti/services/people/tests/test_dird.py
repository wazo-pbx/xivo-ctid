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

from mock import Mock, patch
from unittest import TestCase
from xivo_cti.scheduler import Scheduler

from ..dird import Dird


@patch('os.write', Mock())
class TestDird(TestCase):

    def setUp(self):
        self.scheduler = Scheduler()
        self.scheduler.setup(Mock())
        self.dird = Dird(self.scheduler)

    @patch('requests.get')
    def test_headers(self, http_get):
        callback = Mock()
        profile = 'my_profile'
        expected_url = 'http://localhost:50060/0.1/directories/lookup/{profile}/headers'.format(profile=profile)
        headers, types = ["Fìrstname", "Làstname", "Phòne number"], [None, None, "office"]
        http_get.return_value = Mock(
            content=json.dumps(
                {
                    "column_headers": headers,
                    "column_types": types
                }
            )
        )
        decoded_result = {
            "column_headers": _unicode_list(headers),
            "column_types": _unicode_list(types)
        }

        self.dird.headers(profile, callback)

        self.dird.executor.shutdown(wait=True)
        http_get.assert_called_once_with(expected_url)
        callback.assert_called_once_with(decoded_result)


def _unicode_list(binary_list):
    result = []
    for binary_element in binary_list:
        if binary_element:
            result.append(binary_element.decode('utf8'))
        else:  # may contain None
            result.append(binary_element)
    return result
