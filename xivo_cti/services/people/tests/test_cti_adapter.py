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


from mock import Mock, patch, sentinel as s
from mock import ANY
from unittest import TestCase

from xivo_cti import dao

from ..cti_adapter import PeopleCTIAdapter


class TestCTIAdapter(TestCase):

    def setUp(self):
        self.dird = Mock()
        self.cti_server = Mock()
        self.cti_adapter = PeopleCTIAdapter(self.dird, self.cti_server)

    @patch('xivo_cti.dao.user', Mock())
    def test_get_headers(self):
        dao.user.get_context = Mock(return_value=s.profile)

        self.cti_adapter.get_headers(s.user_id)

        self.dird.headers.assert_called_once_with(s.profile, ANY)

    def test_send_headers_result(self):
        user_id = 12
        headers = {
            'column_headers': Mock(),
            'column_types': Mock(),
        }

        self.cti_adapter._send_headers_result(user_id, headers)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12',
            {
                'class': 'people_headers_result',
                'column_headers': headers['column_headers'],
                'column_types': headers['column_types']
            }
        )
