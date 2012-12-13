# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
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
from mock import Mock


class TestAMICallbackHandler(unittest.TestCase):

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
        event_1 = self._new_event(event_1_name)
        event_2 = self._new_event(event_2_name)
        log_function = Mock()
        newchannel_function = Mock()

        self.handler.register_callback(event_1_name, log_function)
        self.handler.register_callback(event_2_name, log_function)
        self.handler.register_callback(event_2_name, newchannel_function)

        callbacks_1 = self.handler.get_callbacks(event_1)
        callbacks_2 = self.handler.get_callbacks(event_2)
        empty_callback = self.handler.get_callbacks(self._new_event('NoCallbackEvent'))

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

        self.assertEqual(self.handler._callbacks, {event_name.lower(): list([f2])})

    def test_callback_order(self):
        event_name = 'ATestEvent'
        event = self._new_event(event_name)

        def f1(event):
            pass

        def f2(event):
            pass

        self.handler.register_callback(event_name, f1)
        self.handler.register_callback(event_name, f2)
        expected_callbacks = [f1, f2]

        callbacks = self.handler.get_callbacks(event)

        self.assertEqual(callbacks, expected_callbacks)

    def test_userevent_callback(self):
        userevent_name = 'Foobar'
        callback = Mock()
        self.handler.register_userevent_callback(userevent_name, callback)

        callbacks = self.handler.get_callbacks(self._new_userevent(userevent_name))

        self.assertEqual([callback], callbacks)

    def test_subscribe_to_generic_userevent(self):
        userevent_name = 'Foobar'
        callback1 = Mock()
        callback2 = Mock()

        self.handler.register_callback('UserEvent', callback1)
        self.handler.register_userevent_callback(userevent_name, callback2)

        callbacks = self.handler.get_callbacks(self._new_userevent(userevent_name))

        self.assertEqual(sorted([callback1, callback2]), sorted(callbacks))

    def _new_event(self, event_name):
        return {'Event': event_name}

    def _new_userevent(self, userevent_name):
        return {'Event': 'UserEvent', 'UserEvent': userevent_name}
