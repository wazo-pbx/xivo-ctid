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

import unittest

from mock import patch
from mock import Mock
from xivo_cti.xivo_ami import AMIClass
from xivo_cti.services.device.controller.aastra import AastraController
from xivo_dao.data_handler.device.model import Device


class TestAastraController(unittest.TestCase):

    def setUp(self):
        self._ami_class = Mock(AMIClass)

    @patch('xivo_dao.line_dao.get_peer_name')
    def test_answer(self, mock_get_peer_name):
        peer = 'SIP/1234'
        device = Device(id=13)

        mock_get_peer_name.return_value = peer

        aastra_controller = AastraController(self._ami_class)
        aastra_controller.answer(device)

        var_content = {'Content': '<AastraIPPhoneExecute><ExecuteItem URI=\\"Key:Line1\\"/></AastraIPPhoneExecute>',
                       'Event': 'aastra-xml',
                       'Content-type': 'application/xml'}

        self._ami_class.sipnotify.assert_called_once_with(peer, var_content)
