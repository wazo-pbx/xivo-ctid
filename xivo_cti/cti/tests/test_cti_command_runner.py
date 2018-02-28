# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock
from xivo_cti.cti.cti_command import CTICommandInstance
from xivo_cti.cti.cti_command_runner import CTICommandRunner
from xivo_cti.exception import InvalidCallbackException


class Test(unittest.TestCase):

    def setUp(self):
        self.handler = Mock()
        self.handler.return_value = None
        self.command = Mock()
        self.command.callbacks_with_params.return_value = [(self.handler, ['abc'])]
        self.runner = CTICommandRunner()

    def test_run_command(self):
        reply = self.runner.run(self.command)

        self.command.callbacks_with_params.assert_called_once_with()
        self.handler.assert_called_once_with(self.command.abc)
        self.assertEqual(reply, {"status": "OK"})

    def test_run_command_typo(self):
        command = CTICommandInstance()
        command.callbacks_with_params = lambda: [(self.handler, ['abc'])]

        self.assertRaises(AttributeError, self.runner.run, command)

    def test_run_replies(self):
        self.handler.return_value = 'message', {'color': 'red'}

        reply = self.runner.run(self.command)

        self.command.callbacks_with_params.assert_called_once_with()
        self.handler.assert_called_once_with(self.command.abc)
        self.assertEqual(reply, {'message': {'color': 'red'},
                                 'replyid': self.command.commandid,
                                 'class': self.command.command_class})

    def test_run_command_invalid_callback(self):
        self.handler.side_effect = InvalidCallbackException()

        try:
            self.runner.run(self.command)
        except InvalidCallbackException:
            self.fail('CTICommandRunner.run() should not raise InvalidCallbackException')

        self.command.deregister_callback.assert_called_once_with(self.handler)
