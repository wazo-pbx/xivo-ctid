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
import mock
import unittest

from xivo_cti.cti.cti_message_encoder import CTIMessageEncoder


class TestCTIMessageEncoder(unittest.TestCase):

    def setUp(self):
        self.time = 123
        self.cti_msg_encoder = CTIMessageEncoder()

    @mock.patch('time.time')
    def test_encode(self, mock_time):
        mock_time.return_value = self.time
        msg = {'class': 'foo'}
        expected_msg = {'class': 'foo', 'timenow': self.time}

        encoded_msg = self.cti_msg_encoder.encode(msg)

        self.assertTrue(encoded_msg.endswith('\n'))
        self.assertEqual(expected_msg, json.loads(encoded_msg[:-1]))
