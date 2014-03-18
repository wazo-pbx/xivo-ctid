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
from mock import Mock
from xivo_cti.cti.cti_command import CTICommandInstance
from xivo_cti.cti.cti_command_runner import CTICommandRunner


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
