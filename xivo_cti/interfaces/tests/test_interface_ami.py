# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

from mock import Mock, patch, sentinel
from xivo_cti.interfaces.interface_ami import AMI


class TestInterfaceAMI(unittest.TestCase):

    def setUp(self):
        self.context_patcher = patch('xivo_cti.interfaces.interface_ami.context')
        self.context = self.context_patcher.start()

        self.ami_callback_handler_patcher = patch('xivo_cti.interfaces.interface_ami.ami_callback_handler')
        self.ami_callback_handler = self.ami_callback_handler_patcher.start()

        self.cti_server = Mock()

        self.ami = AMI(self.cti_server, Mock(), Mock())

    def tearDown(self):
        self.context_patcher.stop()
        self.ami_callback_handler_patcher.stop()

    def setup_handle_ami_function(self):
        handler = Mock()
        self.ami_callback_handler.AMICallbackHandler = handler

        instance = Mock()
        handler.get_instance.return_value = instance

        callback = Mock()
        callbacks = [callback]
        instance.get_callbacks.return_value = callbacks

        ami_18 = Mock()
        self.context.get.return_value = ami_18

        return handler, instance, callback, ami_18

    def test_decode_raw_event(self):
        raw_event = 'Event: Foobar\r\nCallerIDName: LASTNAME Firstnam\xe9\r\n'
        expected = u'Event: Foobar\r\nCallerIDName: LASTNAME Firstnam\ufffd\r\n'

        result = self.ami.decode_raw_event(raw_event)

        self.assertEquals(result, expected)

    def test_handle_ami_function_calls_callback_from_ami_callback_handler(self):
        _, instance, _, _ = self.setup_handle_ami_function()
        event = {'Event': 'Foobar'}

        self.ami.handle_ami_function(event['Event'], event)

        instance.get_callbacks.assert_called_once_with(event)

    def test_handle_ami_funtion_calls_ami_method(self):
        _, _, _, ami_18 = self.setup_handle_ami_function()
        event = {'Event': 'Foobar'}
        ami_18.ami_foobar = Mock()

        self.ami.handle_ami_function(event['Event'], event)

        ami_18.ami_foobar.assert_called_once_with(event)

    def test_run_functions_with_one_param(self):
        f1, f2, f3 = functions = [
            Mock(),
            Mock(),
            Mock(),
        ]

        self.ami._run_functions_with_event(functions, sentinel.param)

        f1.assert_called_once_with(sentinel.param)
        f2.assert_called_once_with(sentinel.param)
        f3.assert_called_once_with(sentinel.param)

    def test_run_functions_with_exceptions_in_function(self):
        f1, f2, f3 = functions = [
            Mock(),
            Mock(side_effect=Exception),
            Mock(),
        ]

        self.ami._run_functions_with_event(functions, sentinel.param)

        f1.assert_called_once_with(sentinel.param)
        f2.assert_called_once_with(sentinel.param)
        f3.assert_called_once_with(sentinel.param)
