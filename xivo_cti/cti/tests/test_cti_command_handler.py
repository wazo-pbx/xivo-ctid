# -*- coding: utf-8 -*-
# Copyright (C) 2007-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, patch

from xivo_cti.ctiserver import CTIServer
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.cti.cti_command_handler import CTICommandHandler
from xivo_cti.cti.commands.dial import Dial
from xivo_cti.cti.cti_command import CTICommandInstance
from xivo_cti.cti.cti_message_codec import CTIMessageDecoder,\
    CTIMessageEncoder


class TestCTICommandHandler(unittest.TestCase):

    def setUp(self):
        self._msg_1 = {"class": "ipbxcommand",
                       "command": "dial",
                       "commandid": 737000717,
                       "destination": "1004"}
        self._ctiserver = Mock(CTIServer, myipbxid='xivo')
        with patch('xivo_cti.interfaces.interface_cti.context', Mock()):
            with patch('xivo_cti.interfaces.interface_cti.AuthenticationHandler', Mock()):
                self._cti_connection = CTI(self._ctiserver, Mock(), CTIMessageDecoder(), CTIMessageEncoder())

    def test_parse_message(self):
        cti_handler = CTICommandHandler(self._cti_connection)

        self.assertEqual(len(cti_handler._commands_to_run), 0)

        cti_handler.parse_message(self._msg_1)

        self.assertEqual(len(cti_handler._commands_to_run), 1)
        command = cti_handler._commands_to_run[0]
        self.assertTrue(command.command_class, Dial.class_name)

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
