# -*- coding: utf-8 -*-
# Copyright (C) 2007-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from xivo_cti.tools import weak_method
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

    def test_deregister_callback_unwrapped(self):
        command_class = CTICommandClass(self.class_name, None, None)
        command = command_class.from_dict({'class': 'callback_test'})

        function_1 = lambda: None
        function_2 = lambda: None

        command_class.register_callback_params(function_1)
        command_class.register_callback_params(function_2)
        command_class.deregister_callback(function_1)

        callbacks = command.callbacks_with_params()
        self.assertEqual(len(callbacks), 1)
        self.assertEqual(weak_method.WeakCallable(function_2), callbacks[0][0])

    def test_deregister_callback_wrapped(self):
        command_class = CTICommandClass(self.class_name, None, None)
        command = command_class.from_dict({'class': 'callback_test'})

        function_1 = lambda: None
        function_2 = lambda: None

        command_class.register_callback_params(function_1)
        command_class.register_callback_params(function_2)
        command_class.deregister_callback(command.callbacks_with_params()[0][0])

        callbacks = command.callbacks_with_params()
        self.assertEqual(len(callbacks), 1)
        self.assertEqual(weak_method.WeakCallable(function_2), callbacks[0][0])
