# vim: set fileencoding=utf-8 :
# xivo-ctid

# Copyright (C) 2007-2012  Avencall
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

from xivo_cti.ami import ami_callback_handler
from tests.mock import Mock


class Test(unittest.TestCase):

    def setUp(self):
        self.handler = ami_callback_handler.AMICallbackHandler.get_instance()

    def tearDown(self):
        ami_callback_handler.AMICallbackHandler._instance = None

    def test_ami_callback_handler(self):
        handler_1 = ami_callback_handler.AMICallbackHandler.get_instance()

        self.assertTrue(isinstance(handler_1, ami_callback_handler.AMICallbackHandler))
        self.assertEqual(handler_1, ami_callback_handler.AMICallbackHandler._instance)

        handler_2 = ami_callback_handler.AMICallbackHandler.get_instance()

        self.assertEqual(handler_2, handler_1)

    def test_register_callback(self):
        self.assertEqual(self.handler._callbacks, {})
        event_name = 'ATestEvent'

        def a_function(event):
            pass

        self.handler.register_callback(event_name, a_function)

        self.assertEqual(len(self.handler._callbacks), 1)
        self.assertTrue(event_name.lower() in self.handler._callbacks)
        callbacks = self.handler._callbacks[event_name.lower()]
        self.assertEqual(len(callbacks), 1)

        self.handler.register_callback(event_name, a_function)

        self.assertEqual(len(self.handler._callbacks), 1)
        self.assertTrue(event_name.lower() in self.handler._callbacks)
        callbacks = self.handler._callbacks[event_name.lower()]
        self.assertEqual(len(callbacks), 1)

        def another_function(event):
            pass

        self.handler.register_callback(event_name, another_function)

        self.assertEqual(len(self.handler._callbacks), 1)
        self.assertTrue(event_name.lower() in self.handler._callbacks)
        callbacks = self.handler._callbacks[event_name.lower()]
        self.assertEqual(len(callbacks), 2)

    def test_get_callbacks(self):
        event_1_name = 'TestEvent'
        event_2_name = 'NewChannel'
        log_function = Mock()
        newchannel_function = Mock()

        self.handler.register_callback(event_1_name, log_function)
        self.handler.register_callback(event_2_name, log_function)
        self.handler.register_callback(event_2_name, newchannel_function)

        callbacks_1 = self.handler.get_callbacks(event_1_name)
        callbacks_2 = self.handler.get_callbacks(event_2_name)
        empty_callback = self.handler.get_callbacks('NoCallbackEvent')

        self.assertEqual(callbacks_1, [log_function])
        self.assertEqual(len(callbacks_1), 1)
        self.assertTrue(log_function in callbacks_2 and newchannel_function in callbacks_2)
        self.assertEqual(len(callbacks_2), 2)
        self.assertEqual(empty_callback, [])

    def test_unregister_callback(self):
        event_name = 'ATestEvent'

        def a_function(event):
            pass

        self.handler.register_callback(event_name, a_function)
        self.handler.unregister_callback(event_name, a_function)

        self.assertEqual(self.handler._callbacks, {})

    def test_unregister_callback_multiple_registration(self):
        event_name = 'ATestEvent'

        def f1(event):
            pass

        def f2(event):
            pass

        self.handler.register_callback(event_name, f1)
        self.handler.register_callback(event_name, f2)

        self.handler.unregister_callback(event_name, f1)

        self.assertEqual(self.handler._callbacks, {event_name.lower(): set([f2])})
