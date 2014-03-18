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

from mock import Mock
from xivo_cti.ctiserver import CTIServer
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.cti.cti_command_handler import CTICommandHandler
from xivo_cti.cti.commands.invite_confroom import InviteConfroom
from xivo_cti.cti.cti_command import CTICommandInstance


class TestCTICommandHandler(unittest.TestCase):

    def setUp(self):
        self._msg_1 = {"class": "invite_confroom",
                       "commandid": 737000717,
                       "invitee": "user:pcmdev/3"}
        self._ctiserver = Mock(CTIServer)
        self._cti_connection = CTI(self._ctiserver)

    def test_parse_message(self):
        cti_handler = CTICommandHandler(self._cti_connection)

        self.assertEqual(len(cti_handler._commands_to_run), 0)

        cti_handler.parse_message(self._msg_1)

        self.assertEqual(len(cti_handler._commands_to_run), 1)
        command = cti_handler._commands_to_run[0]
        self.assertTrue(command.command_class, InviteConfroom.class_name)

    def test_run_command(self):
        self.called = False

        def func(x, y):
            self.called = x == 'test name' and y == 25

        command = CTICommandInstance()
        command.name = 'test name'
        command.age = 25
        command.callbacks_with_params = lambda: [(func, ['name', 'age'])]
        handler = CTICommandHandler(self._cti_connection)
        handler._commands_to_run.append(command)

        handler.run_commands()

        self.assertTrue(self.called)
