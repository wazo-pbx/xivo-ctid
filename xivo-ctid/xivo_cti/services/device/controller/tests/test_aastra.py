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

import unittest

from mock import patch
from xivo_cti.services.device.controller.aastra import AastraController


class TestAastraController(unittest.TestCase):

    @patch('xivo_dao.line_dao.get_peer_name')
    def test_answer(self, mock_get_peer_name):
        device_id = 66
        peer = 'SIP/1234'

        mock_get_peer_name.return_value = peer

        aastra_controller = AastraController()

        result = aastra_controller.answer(device_id)

        var_content = {'Content': '<AastraIPPhoneExecute><ExecuteItem URI=\\"Key:Line1\\"/></AastraIPPhoneExecute>',
                       'Event': 'aastra-xml',
                       'Content-type': 'application/xml'}

        expected_result = (peer, var_content)

        self.assertEqual(result, expected_result)

    @patch('xivo_dao.line_dao.get_peer_name')
    def test_answer_good_peer(self, mock_get_peer_name):
        device_id = 66
        peer = 'SIP/abcde'

        mock_get_peer_name.return_value = peer

        aastra_controller = AastraController()

        result = aastra_controller.answer(device_id)

        var_content = {'Content': '<AastraIPPhoneExecute><ExecuteItem URI=\\"Key:Line1\\"/></AastraIPPhoneExecute>',
                       'Event': 'aastra-xml',
                       'Content-type': 'application/xml'}

        expected_result = (peer, var_content)

        self.assertEqual(result, expected_result)
