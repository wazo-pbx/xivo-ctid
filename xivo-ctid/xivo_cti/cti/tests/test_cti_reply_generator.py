# -*- coding: UTF-8 -*-

import unittest
from xivo_cti.cti_config import CTI_PROTOCOL_VERSION
from xivo_cti.cti.commands.login_id import LoginID
from xivo_cti.cti.cti_reply_generator import CTIReplyGenerator


class TestCTIReplyGenerator(unittest.TestCase):

    def test_get_reply(self):
        command_id = 926248379
        session_id = "DgUW9T0PYw"
        xivo_version = CTI_PROTOCOL_VERSION
        login_id = LoginID()
        login_id.commandid = command_id
        login_id.xivo_version = xivo_version
        message = {'sessionid': session_id, 'version': '9999', 'replyid': command_id, 'class': 'login_id', 'xivoversion': xivo_version}
        expected = {'message': message, 'replyid': command_id, 'class': 'login_id'}

        generator = CTIReplyGenerator()

        reply = generator.get_reply('message', login_id, message)

        self.assertEqual(reply, expected)
