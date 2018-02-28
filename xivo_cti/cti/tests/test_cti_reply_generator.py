# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from xivo_cti import CTI_PROTOCOL_VERSION
from xivo_cti.cti.cti_reply_generator import CTIReplyGenerator
from xivo_cti.cti.cti_command import CTICommandInstance


class TestCTIReplyGenerator(unittest.TestCase):

    def test_get_reply(self):
        command_id = 926248379
        session_id = "DgUW9T0PYw"
        xivo_version = CTI_PROTOCOL_VERSION
        login_id = CTICommandInstance()
        login_id.commandid = command_id
        login_id.command_class = 'foobar'
        login_id.xivo_version = xivo_version
        message = {'sessionid': session_id, 'version': '9999', 'replyid': command_id, 'class': 'foobar', 'wazoversion': xivo_version}
        expected = {'message': message, 'replyid': command_id, 'class': 'foobar'}

        generator = CTIReplyGenerator()

        reply = generator.get_reply('message', login_id, message)

        self.assertEqual(reply, expected)
