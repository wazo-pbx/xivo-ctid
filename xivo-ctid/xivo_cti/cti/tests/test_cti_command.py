# vim: set fileencoding=utf-8 :
# XiVO CTI Server

# Copyright (C) 2007-2011  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.missing_field_exception import MissingFieldException
from tests.mock import Mock
import weakref
from xivo_cti.tools import weak_method


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        CTICommand._callbacks = []

    def test_cti_command(self):
        cti_command = CTICommand()

        self.assertEqual(cti_command.commandid, None)
        self.assertEqual(cti_command.command_class, None)
        self.assertEqual(cti_command._msg, None)

    def test_from_dict(self):
        command_class = u'test_command'
        commandid = '12345'
        cti_command = CTICommand.from_dict({'class': command_class, 'commandid': commandid})

        self.assertEqual(cti_command.commandid, commandid)
        self.assertEqual(cti_command.command_class, command_class)
        self.assertEqual(cti_command.cti_connection, None)

        self.assertEqual(len(CTICommand.required_fields), 1)

    def test_required_fields(self):
        try:
            cti_command = CTICommand()
            cti_command._init_from_dict({})
            self.assertTrue(False, u'Should raise an exception')
        except MissingFieldException:
            self.assertTrue(True, u'Should raise an exception')

        try:
            command_class = u'test_command'
            CTICommand.from_dict({'class': command_class})
            self.assertTrue(True, u'Should not raise an exception')
        except MissingFieldException:
            self.assertTrue(False, u'Should raise an exception')

    def test_match_message(self):
        self.assertFalse(CTICommand.match_message({}))

        CTICommand.conditions = [('class', 'test_command'), ('value', 'to_match')]
        self.assertTrue(CTICommand.match_message({'class': 'test_command', 'value': 'to_match'}))
        self.assertTrue(CTICommand.match_message({'class': 'test_command', 'value': 'to_match', 'other': 'not_checked'}))
        self.assertFalse(CTICommand.match_message({'class': 'test_command'}))

    def test_register_callback(self):
        command = CTICommand().from_dict({'class': 'callback_test'})

        self.assertEqual(command.callbacks(), [])

        function = Mock()
        CTICommand.register_callback(function)

        command = CTICommand.from_dict({'class': 'callback_test'})
        self.assertEqual(len(command.callbacks()), 1)

    def test_callback_memory_usage(self):
        class Test(object):
            def __init__(self):
                CTICommand.register_callback(self.parse)

            def parse(self):
                pass

        command = CTICommand.from_dict({CTICommand.CLASS: 'callback_test'})

        def run_test():
            self.assertEqual(len(command.callbacks()), 0)
            test_object = Test()
            self.assertEqual(len(command.callbacks()), 1)
            test_object.parse()

        run_test()

        self.assertEqual(len(command.callbacks()), 0)

    def test_get_reply(self):
        command_class = 'return_test'
        command = CTICommand.from_dict({'class': command_class})
        command.command_class = command_class

        reply = command.get_reply('message', {'message': 'This is the test message'}, close_connection=False)

        self.assertFalse('closemenow' in reply)
        self.assertTrue('message' in reply)
        self.assertEqual(reply['message']['message'], 'This is the test message')
        self.assertEqual(reply['class'], command_class)
        self.assertFalse('replyid' in reply)

        commandid = '12345'
        command.commandid = commandid

        reply = command.get_reply('message', 'Test 2', True)

        self.assertTrue('closemenow' in reply)
        self.assertEqual(reply['replyid'], commandid)

    def test_get_warning(self):
        command_class = 'warning_test'
        command = CTICommand.from_dict({'class': command_class})
        command.command_class = command_class

        reply = command.get_warning({'message': 'Unknown command'})

        self.assertTrue('warning' in reply)
        self.assertEqual(reply['warning']['message'], 'Unknown command')

    def test_get_message(self):
        command_class = 'message_test'
        command = CTICommand.from_dict({'class': command_class})
        command.command_class = command_class

        reply = command.get_message({'message': 'Test completed successfully'}, True)

        self.assertTrue('closemenow' in reply, 'closemenow should be present when passing close_connection -> True')
        self.assertTrue('message' in reply)
        self.assertEqual(reply['message']['message'], 'Test completed successfully')