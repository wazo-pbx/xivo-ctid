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
from xivo.asterisk.extension import Extension
from xivo_cti.model.endpoint_status import EndpointStatus
from xivo_cti.model.call_event import CallEvent
from xivo_cti.services.call.notifier import CallNotifier
from xivo_cti.services.call.storage import CallStorage


class TestCallStorage(unittest.TestCase):

    def setUp(self):
        self.notifier = Mock(CallNotifier)
        self.storage = CallStorage(self.notifier)

    def test_update_endpoint_status(self):
        extension = Extension('1234', 'my_context')
        status = EndpointStatus.ringing
        expected_event = CallEvent(extension, status)

        self.storage.update_endpoint_status(extension, status)

        self.notifier.notify.assert_called_once_with(expected_event)

    def test_update_endpoint_status_called_twice_same_status(self):
        extension = Extension('1234', 'my_context')
        status = EndpointStatus.ringing
        expected_event = CallEvent(extension, status)

        self.storage.update_endpoint_status(extension, status)
        self.storage.update_endpoint_status(extension, status)

        self.notifier.notify.assert_called_once_with(expected_event)

    def test_update_endpoint_status_called_twice_different_status(self):
        extension = Extension('1234', 'my_context')

        first_status = EndpointStatus.available
        second_status = EndpointStatus.ringing

        first_event = CallEvent(extension, first_status)
        second_event = CallEvent(extension, second_status)

        self.storage.update_endpoint_status(extension, first_status)
        self.storage.update_endpoint_status(extension, second_status)

        self.notifier.notify.assert_any_call(first_event)
        self.notifier.notify.assert_any_call(second_event)

    def test_update_endpoint_status_2_different_extensions(self):
        first_extension = Extension('1234', 'my_context')
        second_extension = Extension('5678', 'my_context')

        status = EndpointStatus.ringing

        first_expected_event = CallEvent(first_extension, status)
        second_expected_event = CallEvent(second_extension, status)

        self.storage.update_endpoint_status(first_extension, status)
        self.storage.update_endpoint_status(second_extension, status)

        self.notifier.notify.assert_any_call(first_expected_event)
        self.notifier.notify.assert_any_call(second_expected_event)

    def test_update_endpoint_status_same_extension_different_context(self):
        first_extension = Extension('1234', 'my_context')
        second_extension = Extension('1234', 'other_context')

        status = EndpointStatus.ringing

        first_expected_event = CallEvent(first_extension, status)
        second_expected_event = CallEvent(second_extension, status)

        self.storage.update_endpoint_status(first_extension, status)
        self.storage.update_endpoint_status(second_extension, status)

        self.notifier.notify.assert_any_call(first_expected_event)
        self.notifier.notify.assert_any_call(second_expected_event)

    def test_get_status_for_extension(self):
        extension = Extension('1234', 'ze_context')

        expected_status = EndpointStatus.available

        result = self.storage.get_status_for_extension(extension)

        self.assertEquals(expected_status, result)

    def test_get_status_for_extension_during_call(self):
        extension = Extension('1234', 'ze_context')
        status = EndpointStatus.ringing

        self.storage.update_endpoint_status(extension, status)
        result = self.storage.get_status_for_extension(extension)

        self.assertEquals(status, result)

    def test_get_status_for_extension_after_call(self):
        extension = Extension('1234', 'ze_context')
        during_call_status = EndpointStatus.ringing
        after_call_status = EndpointStatus.available

        self.storage.update_endpoint_status(extension, during_call_status)
        self.storage.update_endpoint_status(extension, after_call_status)

        result = self.storage.get_status_for_extension(extension)

        self.assertEquals(after_call_status, result)
