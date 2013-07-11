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
from xivo_cti.model.endpoint_event import EndpointEvent
from xivo_cti.model.endpoint_status import EndpointStatus
from xivo_cti.model.call_event import CallEvent
from xivo_cti.model.call_status import CallStatus
from xivo_cti.services.call.call_notifier import CallNotifier
from xivo_cti.services.call.endpoint_notifier import EndpointNotifier
from xivo_cti.services.call.storage import Call
from xivo_cti.services.call.storage import CallStorage

NUMBER = '1234'
CONTEXT = 'ze_context'
EXTENSION = Mock(number=NUMBER, context=CONTEXT)
SOURCE = Mock(number='2398', context='ze_context')
DESTINATION = Mock(number='3297', context='ze_context')
UNIQUEID = '8976549874.84'


class TestCallStorage(unittest.TestCase):

    def setUp(self):
        self.endpoint_notifier = Mock(EndpointNotifier)
        self.call_notifier = Mock(CallNotifier)
        self.storage = CallStorage(self.endpoint_notifier, self.call_notifier)

    def test_update_endpoint_status(self):
        status = EndpointStatus.ringing
        calls = [self._create_call(source=EXTENSION)]
        expected_event = EndpointEvent(EXTENSION, status, calls)

        self.storage.update_endpoint_status(EXTENSION, status)

        self.endpoint_notifier.notify.assert_called_once_with(expected_event)

    def test_update_endpoint_status_called_twice_same_status(self):
        status = EndpointStatus.ringing
        calls = [self._create_call(source=EXTENSION)]
        expected_event = EndpointEvent(EXTENSION, status, calls)

        self.storage.update_endpoint_status(EXTENSION, status)
        self.storage.update_endpoint_status(EXTENSION, status)

        self.endpoint_notifier.notify.assert_called_once_with(expected_event)

    def test_update_endpoint_status_called_twice_different_status(self):
        calls = [self._create_call(source=EXTENSION)]

        first_status = EndpointStatus.available
        second_status = EndpointStatus.ringing

        first_event = EndpointEvent(EXTENSION, first_status, calls)
        second_event = EndpointEvent(EXTENSION, second_status, calls)

        self.storage.update_endpoint_status(EXTENSION, first_status)
        self.storage.update_endpoint_status(EXTENSION, second_status)

        self.endpoint_notifier.notify.assert_any_call(first_event)
        self.endpoint_notifier.notify.assert_any_call(second_event)

    def test_update_endpoint_status_2_different_extensions(self):
        first_extension = Mock(number='1234', context='my_context')
        second_extension = Mock(number='5678', context='my_context')

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
        first_extension = Mock(number='1234', context='my_context')
        second_extension = Mock(number='1234', context='other_context')

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
        expected_status = EndpointStatus.available

        result = self.storage.get_status_for_extension(EXTENSION)

        self.assertEquals(expected_status, result)

    def test_get_status_for_extension_during_call(self):
        status = EndpointStatus.ringing

        self.storage.update_endpoint_status(EXTENSION, status)
        result = self.storage.get_status_for_extension(EXTENSION)

        self.assertEquals(status, result)

    def test_get_status_for_extension_after_call(self):
        during_call_status = EndpointStatus.ringing
        after_call_status = EndpointStatus.available

        self.storage.update_endpoint_status(EXTENSION, during_call_status)
        self.storage.update_endpoint_status(EXTENSION, after_call_status)

        result = self.storage.get_status_for_extension(EXTENSION)

        self.assertEquals(after_call_status, result)

    def test_find_all_calls_for_extension_when_no_calls(self):
        expected_calls = []

        result = self.storage.find_all_calls_for_extension(EXTENSION)

        self.assertEquals(expected_calls, result)

    def test_find_all_calls_for_extension_when_calls_received(self):
        expected_calls = [Call(SOURCE, DESTINATION)]

        self.storage.new_call(UNIQUEID, SOURCE, DESTINATION)
        result = self.storage.find_all_calls_for_extension(SOURCE)

        self.assertEquals(expected_calls, result)

    def test_find_all_calls_for_extension_when_calls_emitted(self):
        expected_calls = [Call(SOURCE, DESTINATION)]

        self.storage.new_call(UNIQUEID, SOURCE, DESTINATION)
        result = self.storage.find_all_calls_for_extension(DESTINATION)

        self.assertEquals(expected_calls, result)

    def test_find_all_calls_for_extension_when_calls_do_not_concern_extension(self):
        extension = Mock(number='1234', context='ze_context')
        expected_calls = []

        self.storage.new_call(UNIQUEID, SOURCE, DESTINATION)
        result = self.storage.find_all_calls_for_extension(extension)

        self.assertEquals(expected_calls, result)

    def test_new_call(self):
        status = CallStatus.ringing
        expected_call_event = CallEvent(UNIQUEID, SOURCE, DESTINATION, status)

        self.storage.new_call(UNIQUEID, SOURCE, DESTINATION)

        self.call_notifier.notify.assert_called_once_with(expected_call_event)

    def test_new_call_twice(self):
        status = CallStatus.ringing
        expected_event = CallEvent(UNIQUEID, SOURCE, DESTINATION, status)

        self.storage.new_call(UNIQUEID, SOURCE, DESTINATION)
        self.storage.new_call(UNIQUEID, SOURCE, DESTINATION)

        self.call_notifier.notify.assert_called_once_with(expected_event)

    def test_new_call_two_different_calls(self):
        uniqueid_1 = '35732468.66'
        source_1 = Mock(number='3736', context='context_d')
        destination_1 = Mock(number='3257', context='context_d')
        status = CallStatus.ringing
        expected_event_1 = CallEvent(uniqueid_1, source_1, destination_1, status)
        uniqueid_2 = '35732468.99'
        source_2 = Mock(number='2168', context='context_d')
        destination_2 = Mock(number='2156', context='context_d')
        status = CallStatus.ringing
        expected_event_2 = CallEvent(uniqueid_2, source_2, destination_2, status)

        self.storage.new_call(uniqueid_1, source_1, destination_1)
        self.storage.new_call(uniqueid_2, source_2, destination_2)

        self.assertEqual(self.call_notifier.notify.call_count, 2)
        self.call_notifier.notify.assert_any_call(expected_event_1)
        self.call_notifier.notify.assert_any_call(expected_event_2)

    def test_end_call_not_started(self):
        self.storage.end_call(UNIQUEID)

        self.assertEquals(self.call_notifier.notify.call_count, 0)

    def test_end_call_started(self):
        source = Mock(number='3283', context='context_y')
        destination = Mock(number='3258', context='context_y')
        call_status = CallStatus.hangup
        expected_event = CallEvent(UNIQUEID, source, destination, call_status)
        self._create_call(uniqueid=UNIQUEID, source=source, destination=destination)

        self.storage.end_call(UNIQUEID)

        self.assertEquals(self.call_notifier.notify.call_count, 1)
        self.call_notifier.notify.assert_any_call(expected_event)

    def test_end_call_started_once_ended_twice(self):
        source = Mock(number='3283', context='context_y')
        destination = Mock(number='3258', context='context_y')
        status = CallStatus.hangup
        expected_event = CallEvent(UNIQUEID, source, destination, status)
        self._create_call(uniqueid=UNIQUEID, source=source, destination=destination)

        self.storage.end_call(UNIQUEID)
        self.storage.end_call(UNIQUEID)

        self.assertEquals(self.call_notifier.notify.call_count, 1)
        self.call_notifier.notify.assert_any_call(expected_event)

    def _create_call(self, uniqueid=None, source=None, destination=None):
        if not uniqueid:
            uniqueid = Mock()
        if not source:
            source = SOURCE
        if not destination:
            destination = DESTINATION

        self.storage.new_call(uniqueid, source, destination)
        self.call_notifier.reset_mock()
        self.endpoint_notifier.reset_mock()

        return Call(source, destination)
