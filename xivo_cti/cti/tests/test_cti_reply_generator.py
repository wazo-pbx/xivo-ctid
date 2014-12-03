# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
        message = {'sessionid': session_id, 'version': '9999', 'replyid': command_id, 'class': 'foobar', 'xivoversion': xivo_version}
        expected = {'message': message, 'replyid': command_id, 'class': 'foobar'}

        generator = CTIReplyGenerator()

        reply = generator.get_reply('message', login_id, message)

        self.assertEqual(reply, expected)
