# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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
from xivo_cti.cti.cti_command import CTICommandClass


class TestCTICommand(unittest.TestCase):

    def setUp(self):
        self.class_name = 'foo'
        self.commandid = '12345'
        self.msg = {'class': self.class_name, 'commandid': self.commandid}

    def test_from_dict(self):
        command_class = CTICommandClass(self.class_name, None, None)

        command = command_class.from_dict(self.msg)

        self.assertEqual(command.commandid, self.commandid)
        self.assertEqual(command.command_class, self.class_name)

    def test_match_message_when_match_fun_true(self):
        match_fun = Mock()
        match_fun.return_value = True
        command_class = CTICommandClass(self.class_name, match_fun, None)

        self.assertTrue(command_class.match_message({}))
        self.assertTrue(command_class.match_message({'class': self.class_name}))

    def test_match_message_when_match_fun_false(self):
        match_fun = Mock()
        match_fun.return_value = False
        command_class = CTICommandClass(self.class_name, match_fun, None)

        self.assertFalse(command_class.match_message({}))
        self.assertFalse(command_class.match_message({'class': self.class_name}))

    def test_register_callback(self):
        command_class = CTICommandClass(self.class_name, None, None)
        command = command_class.from_dict({'class': 'callback_test'})

        self.assertEqual(command.callbacks_with_params(), [])

        function = Mock()
        command_class.register_callback_params(function)

        command = command_class.from_dict({'class': 'callback_test'})
        self.assertEqual(len(command.callbacks_with_params()), 1)

    def test_callback_memory_usage(self):
        command_class = CTICommandClass(self.class_name, None, None)
        class Test(object):
            def __init__(self):
                command_class.register_callback_params(self.parse)

            def parse(self):
                pass

        command = command_class.from_dict({'class': 'callback_test'})

        def run_test():
            self.assertEqual(len(command.callbacks_with_params()), 0)
            test_object = Test()
            self.assertEqual(len(command.callbacks_with_params()), 1)
            test_object.parse()

        run_test()

        self.assertEqual(len(command.callbacks_with_params()), 0)
