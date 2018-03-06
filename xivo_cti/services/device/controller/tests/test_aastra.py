# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import patch
from mock import Mock
from xivo_cti.model.device import Device
from xivo_cti.services.device.controller.aastra import AastraController
from xivo_cti.xivo_ami import AMIClass


class TestAastraController(unittest.TestCase):

    def setUp(self):
        self.ami_class = Mock(AMIClass)
        self.controller = AastraController(self.ami_class)

    @patch('xivo_dao.line_dao.get_peer_name')
    def test_answer(self, mock_get_peer_name):
        peer = 'SIP/1234'
        device = Device(13)

        mock_get_peer_name.return_value = peer

        self.controller.answer(device)

        var_content = {
            'Content': r'<AastraIPPhoneExecute><ExecuteItem URI=\"Key:Line1\"/></AastraIPPhoneExecute>',
            'Event': 'aastra-xml',
            'Content-type': 'application/xml',
        }

        self.ami_class.sipnotify.assert_called_once_with(peer, var_content)
