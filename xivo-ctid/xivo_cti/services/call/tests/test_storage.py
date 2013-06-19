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
from xivo_cti.model.endpoint_event import EndpointEvent
from xivo_cti.model.endpoint_status import EndpointStatus
from xivo_cti.model.call_event import CallEvent
from xivo_cti.model.call_status import CallStatus
from xivo_cti.services.call.call_notifier import CallNotifier
from xivo_cti.services.call.endpoint_notifier import EndpointNotifier
from xivo_cti.services.call.storage import Call
from xivo_cti.services.call.storage import CallStorage


class TestCallStorage(unittest.TestCase):

    def setUp(self):
        self.endpoint_notifier = Mock(EndpointNotifier)
        self.call_notifier = Mock(CallNotifier)
        self.storage = CallStorage(self.endpoint_notifier, self.call_notifier)

    def test_update_endpoint_status(self):
        extension = Extension('1234', 'my_context')
        status = EndpointStatus.ringing
        calls = [self._create_call(source=extension)]
        expected_event = EndpointEvent(extension, status, calls)

        self.storage.update_endpoint_status(extension, status)

        self.endpoint_notifier.notify.assert_called_once_with(expected_event)

    def test_update_endpoint_status_called_twice_same_status(self):
        extension = Extension('1234', 'my_context')
        status = EndpointStatus.ringing
        calls = [self._create_call(source=extension)]
        expected_event = EndpointEvent(extension, status, calls)

        self.storage.update_endpoint_status(extension, status)
        self.storage.update_endpoint_status(extension, status)

        self.endpoint_notifier.notify.assert_called_once_with(expected_event)

    def test_update_endpoint_status_called_twice_different_status(self):
        extension = Extension('1234', 'my_context')

        calls = [self._create_call(source=extension)]

        first_status = EndpointStatus.available
        second_status = EndpointStatus.ringing

        first_event = EndpointEvent(extension, first_status, calls)
        second_event = EndpointEvent(extension, second_status, calls)

        self.storage.update_endpoint_status(extension, first_status)
        self.storage.update_endpoint_status(extension, second_status)

        self.endpoint_notifier.notify.assert_any_call(first_event)
        self.endpoint_notifier.notify.assert_any_call(second_event)

    def test_update_endpoint_status_2_different_extensions(self):
        first_extension = Extension('1234', 'my_context')
        second_extension = Extension('5678', 'my_context')

        status = EndpointStatus.ringing

        first_extension_calls = [self._create_call(source=first_extension)]
        second_extension_calls = [self._create_call(source=second_extension)]

        first_expected_event = EndpointEvent(first_extension, status, first_extension_calls)
        second_expected_event = EndpointEvent(second_extension, status, second_extension_calls)

        self.storage.update_endpoint_status(first_extension, status)
        self.storage.update_endpoint_status(second_extension, status)

        self.assertEquals(self.endpoint_notifier.notify.call_count, 2)
        self.endpoint_notifier.notify.assert_any_call(first_expected_event)
        self.endpoint_notifier.notify.assert_any_call(second_expected_event)

    def test_update_endpoint_status_same_extension_different_context(self):
        first_extension = Extension('1234', 'my_context')
        second_extension = Extension('1234', 'other_context')

        status = EndpointStatus.ringing

        first_extension_calls = [self._create_call(source=first_extension)]
        second_extension_calls = [self._create_call(source=second_extension)]
        first_expected_event = EndpointEvent(first_extension, status, first_extension_calls)
        second_expected_event = EndpointEvent(second_extension, status, second_extension_calls)

        self.storage.update_endpoint_status(first_extension, status)
        self.storage.update_endpoint_status(second_extension, status)

        self.endpoint_notifier.notify.assert_any_call(first_expected_event)
        self.endpoint_notifier.notify.assert_any_call(second_expected_event)

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

    def test_find_all_calls_for_extension_when_no_extension(self):
        extension = Extension('1234', 'ze_context')
        expected_calls = []

        result = self.storage.find_all_calls_for_extension(extension)

        self.assertEquals(expected_calls, result)

    def test_find_all_calls_for_extension_when_no_calls(self):
        extension = Extension('1234', 'ze_context')
        expected_calls = []

        result = self.storage.find_all_calls_for_extension(extension)

        self.assertEquals(expected_calls, result)

    def test_find_all_calls_for_extension_when_calls_received(self):
        extension = Extension('1234', 'ze_context')
        uniqueid = '293874324.34'
        source = extension
        destination = Extension('2398', 'ze_context')
        expected_calls = [Call(source, destination)]

        self.storage.new_call(uniqueid, source, destination)
        result = self.storage.find_all_calls_for_extension(extension)

        self.assertEquals(expected_calls, result)

    def test_find_all_calls_for_extension_when_calls_emitted(self):
        extension = Extension('1234', 'ze_context')
        uniqueid = '293874324.34'
        source = Extension('2398', 'ze_context')
        destination = extension
        expected_calls = [Call(source, destination)]

        self.storage.new_call(uniqueid, source, destination)
        result = self.storage.find_all_calls_for_extension(extension)

        self.assertEquals(expected_calls, result)

    def test_find_all_calls_for_extension_when_calls_do_not_concern_extension(self):
        extension = Extension('1234', 'ze_context')
        uniqueid = '293874324.34'
        source = Extension('2398', 'ze_context')
        destination = Extension('3297', 'ze_context')
        expected_calls = []

        self.storage.new_call(uniqueid, source, destination)
        result = self.storage.find_all_calls_for_extension(extension)

        self.assertEquals(expected_calls, result)

    def test_new_call(self):
        uniqueid = '564324563.46'
        source = Extension('2335', 'context_x')
        destination = Extension('2324', 'context_x')
        status = CallStatus.ringing
        expected_call_event = CallEvent(uniqueid, source, destination, status)

        self.storage.new_call(uniqueid, source, destination)

        self.call_notifier.notify.assert_called_once_with(expected_call_event)

    def test_new_call_twice(self):
        uniqueid = '348632486.35'
        source = Extension('9835', 'context_c')
        destination = Extension('1416', 'context_c')
        status = CallStatus.ringing
        expected_event = CallEvent(uniqueid, source, destination, status)

        self.storage.new_call(uniqueid, source, destination)
        self.storage.new_call(uniqueid, source, destination)

        self.call_notifier.notify.assert_called_once_with(expected_event)

    def test_new_call_two_different_calls(self):
        uniqueid_1 = '35732468.66'
        source_1 = Extension('3736', 'context_d')
        destination_1 = Extension('3257', 'context_d')
        status = CallStatus.ringing
        expected_event_1 = CallEvent(uniqueid_1, source_1, destination_1, status)
        uniqueid_2 = '35732468.99'
        source_2 = Extension('2168', 'context_d')
        destination_2 = Extension('2156', 'context_d')
        status = CallStatus.ringing
        expected_event_2 = CallEvent(uniqueid_2, source_2, destination_2, status)

        self.storage.new_call(uniqueid_1, source_1, destination_1)
        self.storage.new_call(uniqueid_2, source_2, destination_2)

        self.assertEqual(self.call_notifier.notify.call_count, 2)
        self.call_notifier.notify.assert_any_call(expected_event_1)
        self.call_notifier.notify.assert_any_call(expected_event_2)

    def test_end_call_not_started(self):
        uniqueid = '564324563.46'

        self.storage.end_call(uniqueid)

        self.assertEquals(self.call_notifier.notify.call_count, 0)

    def test_end_call_started(self):
        uniqueid = '653246546.41'
        source = Extension('3283', 'context_y')
        destination = Extension('3258', 'context_y')
        call_status = CallStatus.hangup
        expected_event = CallEvent(uniqueid, source, destination, call_status)
        self._create_call(uniqueid=uniqueid, source=source, destination=destination)

        self.storage.end_call(uniqueid)

        self.assertEquals(self.call_notifier.notify.call_count, 1)
        self.call_notifier.notify.assert_any_call(expected_event)

    def test_end_call_started_once_ended_twice(self):
        uniqueid = '3248646348.46'
        source = Extension('2783', 'context_z')
        destination = Extension('5838', 'context_y')
        status = CallStatus.hangup
        expected_event = CallEvent(uniqueid, source, destination, status)
        self._create_call(uniqueid=uniqueid, source=source, destination=destination)

        self.storage.end_call(uniqueid)
        self.storage.end_call(uniqueid)

        self.assertEquals(self.call_notifier.notify.call_count, 1)
        self.call_notifier.notify.assert_any_call(expected_event)

    def _create_call(self, uniqueid=None, source=None, destination=None):
        if not uniqueid:
            uniqueid = Mock()
        if not source:
            source = Extension('3984', 'my_context')
        if not destination:
            destination = Extension('3973', 'my_context')

        self.storage.new_call(uniqueid, source, destination)
        self.call_notifier.reset_mock()
        self.endpoint_notifier.reset_mock()

        return Call(source, destination)
