# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
from xivo_cti.model.extension import Extension
from xivo_cti.services.call.call_event import CallEvent
from xivo_cti.services.call.notifier import CallNotifier


class TestCallNotifier(unittest.TestCase):

    def setUp(self):
        self.notifier = CallNotifier()

    def test_subscribe_and_notify(self):
        callback = Mock()
        extension = Extension('1000', 'my_context')
        event = Mock(CallEvent)
        event.extension = extension

        self.notifier.subscribe_to_status_changes(extension, callback)

        self.notifier.notify(event)
        callback.assert_called_once_with(event)

    def test_multiple_subscribe_on_same_extension_and_one_notify(self):
        callback_1 = Mock()
        callback_2 = Mock()
        extension = Extension('1000', 'my_context')
        event = Mock(CallEvent)
        event.extension = extension

        self.notifier.subscribe_to_status_changes(extension, callback_1)
        self.notifier.subscribe_to_status_changes(extension, callback_2)

        self.notifier.notify(event)
        callback_1.assert_called_once_with(event)
        callback_2.assert_called_once_with(event)

    def test_multiple_subscribe_on_different_extensions_and_two_notify(self):
        callback = Mock()
        extension_1 = Extension('1000', 'my_context')
        extension_2 = Extension('1001', 'my_other_context')
        event_1 = Mock(CallEvent)
        event_1.extension = extension_1
        event_2 = Mock(CallEvent)
        event_2.extension = extension_2

        self.notifier.subscribe_to_status_changes(extension_1, callback)
        self.notifier.subscribe_to_status_changes(extension_2, callback)

        self.notifier.notify(event_1)
        callback.assert_any_call(event_1)
        self.assertEquals(callback.call_count, 1)

        self.notifier.notify(event_2)
        callback.assert_any_call(event_2)
        self.assertEquals(callback.call_count, 2)

    def test_unsubscribe_when_never_subscribed(self):
        extension = Extension('1000', 'my_context')
        callback = Mock()

        self.notifier.unsubscribe_from_status_changes(extension, callback)

        # Does not raise Exception

    def test_unsubscribed_when_subscribed(self):
        extension = Extension('1000', 'my_context')
        callback = Mock()
        event = Mock(CallEvent)
        event.extension = extension
        self.notifier.subscribe_to_status_changes(extension, callback)

        self.notifier.unsubscribe_from_status_changes(extension, callback)

        self.notifier.notify(event)
        self.assertEquals(callback.call_count, 0)

    def notify_when_nobody_subscribed(self):
        event = Mock(CallEvent)
        event.extension = Extension('1000', 'my_context')

        self.notifier.notify(event)

        # Does not raise Exception

    def test_unsubscribe_when_multiple_subscribers_on_same_extension(self):
        callback_1 = Mock()
        callback_2 = Mock()
        extension = Extension('1000', 'my_context')
        event = Mock(CallEvent)
        event.extension = extension
        self.notifier.subscribe_to_status_changes(extension, callback_1)
        self.notifier.subscribe_to_status_changes(extension, callback_2)

        self.notifier.unsubscribe_from_status_changes(extension, callback_1)

        self.notifier.notify(event)
        self.assertEquals(callback_1.call_count, 0)
        callback_2.assert_called_once_with(event)
