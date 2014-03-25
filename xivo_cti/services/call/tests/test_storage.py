# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from functools import wraps
from hamcrest import assert_that, contains_inanyorder, equal_to, contains, has_item
from mock import Mock
from mock import sentinel, call
from xivo.asterisk.extension import Extension
from xivo_cti.model.endpoint_event import EndpointEvent
from xivo_cti.model.endpoint_status import EndpointStatus
from xivo_cti.model.call_event import CallEvent
from xivo_cti.model.call_status import CallStatus
from xivo_cti.services.call.call_notifier import CallNotifier
from xivo_cti.services.call.endpoint_notifier import EndpointNotifier
from xivo_cti.services.call.storage import Call
from xivo_cti.services.call.call import _Channel
from xivo_cti.services.call.storage import CallStorage

NUMBER = '1234'
CONTEXT = 'ze_context'
EXTENSION = Extension(NUMBER, CONTEXT, is_internal=True)
SOURCE = _Channel(Extension('2398', 'ze_context', is_internal=True), sentinel.source_channel)
DESTINATION = _Channel(Extension('3297', 'ze_context', is_internal=True), sentinel.destination)
UNIQUEID = '8976549874.84'
DEST_UNIQUEID = '6666549874.84'

AVAILABLE = EndpointStatus.available
RINGING = EndpointStatus.ringing


class _BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.endpoint_notifier = Mock(EndpointNotifier)
        self.call_notifier = Mock(CallNotifier)
        self.storage = CallStorage(self.endpoint_notifier, self.call_notifier)

    def _create_call(self, uniqueid=None,
                     destuniqueid=None,
                     source_exten=Mock(Extension),
                     destination_exten=Mock(Extension), source_channel=sentinel.source_channel,
                     destination_channel=sentinel.destination_channel):
        source = _Channel(source_exten, source_channel)
        destination = _Channel(destination_exten, destination_channel)

        self.storage.new_call(uniqueid, destuniqueid, source, destination)

        self.call_notifier.reset_mock()
        self.endpoint_notifier.reset_mock()

        return Call(source, destination)


class TestGetStatusForExtension(_BaseTestCase):

    def test_get_status_for_extension_default_to_available(self):
        result = self.storage.get_status_for_extension(EXTENSION)

        assert_that(result, equal_to(AVAILABLE))

    def test_get_status_for_extension_during_call(self):
        self.storage.update_endpoint_status(EXTENSION, RINGING)

        result = self.storage.get_status_for_extension(EXTENSION)

        assert_that(result, equal_to(RINGING))

    def test_get_status_for_extension_back_to_available_after_call(self):
        self.storage.update_endpoint_status(EXTENSION, RINGING)
        self.storage.update_endpoint_status(EXTENSION, AVAILABLE)

        result = self.storage.get_status_for_extension(EXTENSION)

        assert_that(result, equal_to(AVAILABLE))


def with_default_calls(f):
    '''for TestFindAllCallsForExtension only'''
    @wraps(f)
    def decorator(self, *args, **kwargs):
        self.storage.new_call(UNIQUEID, DEST_UNIQUEID, SOURCE, DESTINATION)
        return f(self, *args, **kwargs)
    return decorator


class TestFindAllCallsForExtension(_BaseTestCase):

    def setUp(self):
        super(TestFindAllCallsForExtension, self).setUp()
        self.default_call = Call(SOURCE, DESTINATION)

    def test_find_all_calls_for_extension_when_no_calls(self):
        result = self.storage.find_all_calls_for_extension(EXTENSION)

        assert_that(result, contains())

    @with_default_calls
    def test_find_all_calls_for_extension_when_calls_received(self):
        result = self.storage.find_all_calls_for_extension(SOURCE.extension)

        assert_that(result, contains(self.default_call))

    @with_default_calls
    def test_find_all_calls_for_extension_when_calls_emitted(self):
        result = self.storage.find_all_calls_for_extension(DESTINATION.extension)

        assert_that(result, contains(self.default_call))

    @with_default_calls
    def test_find_all_calls_for_extension_when_calls_do_not_concern_extension(self):
        extension = Extension('1234', 'ze_context', is_internal=False)

        result = self.storage.find_all_calls_for_extension(extension)

        assert_that(result, contains())


class TestEndCall(_BaseTestCase):

    def setUp(self):
        super(TestEndCall, self).setUp()
        self.source_exten = Extension('3283', 'context_y', is_internal=True)
        self.destination_exten = Extension('3258', 'context_y', is_internal=True)

    def test_end_call_not_started(self):
        self.storage.end_call(UNIQUEID)

        assert_that(self.call_notifier.notify.call_args_list,
                    contains())

    def test_end_call_started(self):
        expected_event = CallEvent(
            uniqueid=UNIQUEID,
            source=self.source_exten,
            destination=self.destination_exten,
            status=CallStatus.hangup,
        )
        self._create_call(uniqueid=UNIQUEID,
                          source_exten=self.source_exten,
                          destination_exten=self.destination_exten)

        self.storage.end_call(UNIQUEID)

        assert_that(self.call_notifier.notify.call_args_list,
                    contains(call(expected_event)))

    def test_end_call_started_once_ended_twice(self):
        expected_event = CallEvent(UNIQUEID,
                                   self.source_exten,
                                   self.destination_exten,
                                   CallStatus.hangup)
        self._create_call(UNIQUEID,
                          source_exten=self.source_exten,
                          destination_exten=self.destination_exten)

        self.storage.end_call(UNIQUEID)
        self.storage.end_call(UNIQUEID)

        assert_that(self.call_notifier.notify.call_args_list,
                    contains(call(expected_event)))


class TestEndpointStatus(_BaseTestCase):

    def setUp(self):
        super(TestEndpointStatus, self).setUp()
        self.calls = [self._create_call(source_exten=EXTENSION)]
        self.ringing_event = EndpointEvent(EXTENSION, RINGING, self.calls)
        self.available_event = EndpointEvent(EXTENSION, AVAILABLE, self.calls)

    def test_when_ringing(self):
        self.storage.update_endpoint_status(EXTENSION, RINGING)

        assert_that(self.endpoint_notifier.notify.call_args_list,
                    contains_inanyorder(call(self.ringing_event)))

    def test_called_twice_with_the_same_status(self):
        self.storage.update_endpoint_status(EXTENSION, RINGING)
        self.storage.update_endpoint_status(EXTENSION, RINGING)

        assert_that(self.endpoint_notifier.notify.call_args_list,
                    contains_inanyorder(call(self.ringing_event)))

    def test_called_twice_with_different_status(self):
        self.storage.update_endpoint_status(EXTENSION, AVAILABLE)
        self.storage.update_endpoint_status(EXTENSION, RINGING)

        assert_that(self.endpoint_notifier.notify.call_args_list,
                    contains(call(self.available_event),
                             call(self.ringing_event)))

    def test_2_different_extensions(self):
        first_extension = Extension(number='1234', context='my_context', is_internal=True)
        second_extension = Extension(number='5678', context='my_context', is_internal=True)

        first_extension_calls = [self._create_call(uniqueid=sentinel.uid1,
                                                   source_exten=first_extension)]
        second_extension_calls = [self._create_call(uniqueid=sentinel.uid2,
                                                    source_exten=second_extension)]

        first_expected_event = EndpointEvent(first_extension, RINGING, first_extension_calls)
        second_expected_event = EndpointEvent(second_extension, RINGING, second_extension_calls)

        self.storage.update_endpoint_status(first_extension, RINGING)
        self.storage.update_endpoint_status(second_extension, RINGING)

        assert_that(self.endpoint_notifier.notify.call_args_list,
                    contains_inanyorder(call(first_expected_event),
                                        call(second_expected_event)))

    def test_same_extension_in_different_context(self):
        first_extension = Extension(number='1234', context='my_context', is_internal=True)
        second_extension = Extension(number='1234', context='other_context', is_internal=True)

        first_extension_calls = [self._create_call(sentinel.uid1, source_exten=first_extension)]
        second_extension_calls = [self._create_call(sentinel.uid2, source_exten=second_extension)]
        first_expected_event = EndpointEvent(first_extension, RINGING, first_extension_calls)
        second_expected_event = EndpointEvent(second_extension, RINGING, second_extension_calls)

        self.storage.update_endpoint_status(first_extension, RINGING)
        self.storage.update_endpoint_status(second_extension, RINGING)

        assert_that(self.endpoint_notifier.notify.call_args_list,
                    contains_inanyorder(call(first_expected_event),
                                        call(second_expected_event)))


class TestNewCall(_BaseTestCase):

    def test_new_call_calls_end_call_and_notify_with_the_fresh_info(self):
        call_event = CallEvent(sentinel.uniqueid,
                               SOURCE.extension,
                               DESTINATION.extension,
                               CallStatus.ringing)
        self.storage.end_call = Mock()

        self.storage.new_call(sentinel.uniqueid, sentinel.dest_uniqueid,
                              SOURCE, DESTINATION)

        self.storage.end_call.assert_any_call(sentinel.uniqueid)
        self.storage.end_call.assert_any_call(sentinel.dest_uniqueid)
        assert_that(self.storage.end_call.call_count, equal_to(2))
        self.call_notifier.notify.assert_called_once_with(call_event)


class TestMergeLocalChannels(_BaseTestCase):

    def test_when_channel_1_is_local(self):
        self.storage._calls = {
            u'1395685236.26': Call(
                _Channel(Extension('1009', 'default', True), 'SIP/1uzh6d-0000000e'),
                _Channel(Extension('', '', True), 'Local/102@default-00000006;1'),
            ),
            u'1395685237.28': Call(
                _Channel(Extension('', '', True), 'Local/102@default-00000006;2'),
                _Channel(Extension('1002', 'default', True), 'SIP/8o5zja-0000000f'),
            ),
        }

        self.storage.merge_local_channels('Local/102@default-00000006;')

        expected = {
            u'1395685237.28': Call(
                _Channel(Extension('1009', 'default', True), 'SIP/1uzh6d-0000000e'),
                _Channel(Extension('1002', 'default', True), 'SIP/8o5zja-0000000f'),
            ),
        }

        assert_that(self.storage._calls, equal_to(expected))
