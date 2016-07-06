# -*- coding: utf-8 -*-

# Copyright (C) 2014-2016 Avencall
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

from concurrent import futures
from hamcrest import assert_that, equal_to
from mock import Mock, patch, sentinel as s
from requests import exceptions

from xivo_cti.ami.ami_callback_handler import AMICallbackHandler
from xivo_cti.async_runner import AsyncRunner, synchronize
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.services.call.manager import CallManager
from xivo_cti.task_queue import new_task_queue
from xivo_cti.xivo_ami import AMIClass


class _BaseTest(unittest.TestCase):

    def setUp(self):
        self._task_queue = new_task_queue()
        self._ami = Mock(AMIClass)
        self._ami_cb_handler = Mock(AMICallbackHandler)
        self._connection = Mock(CTI)
        self._runner = AsyncRunner(futures.ThreadPoolExecutor(max_workers=1), self._task_queue)

        self.manager = CallManager(self._ami, self._ami_cb_handler, self._runner)


class TestCalls(_BaseTest):

    def setUp(self):
        super(TestCalls, self).setUp()
        client_factory = self.manager._new_ctid_ng_client = Mock()
        self.ctid_ng_client = client_factory.return_value

    def test_hangup_with_no_active_call_does_not_crash(self):
        with patch.object(self.manager,
                          '_get_user_active_call',
                          Mock(return_value=None)):
            self.manager.hangup(s.auth_token, s.user_uuid)

    def test_hangup_when_everything_works(self):
        with patch.object(self.manager,
                          '_get_user_active_call',
                          Mock(return_value={'call_id': s.call_id})):
            self.manager.hangup(s.auth_token, s.user_uuid)

        self.ctid_ng_client.calls.hangup_from_user.assert_called_once_with(s.call_id)

    def test_call_exten_success(self):
        call_function = self.ctid_ng_client.calls.make_call_from_user

        with patch.object(self.manager, '_on_call_success') as cb:
            with synchronize(self._runner):
                self.manager.call_exten(s.connection, s.auth_token, s.user_id, s.exten)

        call_function.assert_called_once_with(extension=s.exten)
        cb.assert_called_once_with(s.connection, s.user_id, call_function.return_value)

    def test_call_exten_exception(self):
        call_function = self.ctid_ng_client.calls.make_call_from_user
        exception = call_function.side_effect = Exception()

        with patch.object(self.manager, '_on_call_exception') as cb:
            with synchronize(self._runner):
                self.manager.call_exten(s.connection, s.auth_token, s.user_id, s.exten)

        call_function.assert_called_once_with(extension=s.exten)
        cb.assert_called_once_with(s.connection, s.user_id, s.exten, exception)

    @patch('xivo_cti.services.call.manager.dao')
    def test_on_call_success_with_a_line(self, mock_dao):
        mock_dao.user.get_line_identity.return_value = s.interface

        with patch.object(self.manager, 'answer_next_ringing_call') as answer_next_ringing_call:
            self.manager._on_call_success(s.connection, s.user_id, s.result)

        answer_next_ringing_call.assert_called_once_with(s.connection, s.interface)

    @patch('xivo_cti.services.call.manager.dao')
    def test_on_call_success_with_no_line(self, mock_dao):
        mock_dao.user.get_line_identity.return_value = None

        with patch.object(self.manager, 'answer_next_ringing_call') as answer_next_ringing_call:
            self.manager._on_call_success(s.connection, s.user_id, s.result)

        assert_that(answer_next_ringing_call.call_count, equal_to(0))

    def test_on_call_exception_401(self):
        connection = Mock()
        exception = exceptions.HTTPError(response=Mock(status_code=401))

        self.manager._on_call_exception(connection, s.user_id, s.exten, exception)

        expected_message = CTIMessageFormatter.ipbxcommand_error('calls_unauthorized')
        connection.send_message.assert_called_once_with(expected_message)

    def test_on_call_exception_when_ctid_ng_is_down(self):
        connection = Mock()
        exception = exceptions.ConnectionError()

        self.manager._on_call_exception(connection, s.user_id, s.exten, exception)

        expected_message = CTIMessageFormatter.ipbxcommand_error('service_unavailable')
        connection.send_message.assert_called_once_with(expected_message)

    def test_on_call_exception_when_xivo_auth_is_down(self):
        connection = Mock()
        exception = exceptions.HTTPError(response=Mock(status_code=503))

        self.manager._on_call_exception(connection, s.user_id, s.exten, exception)

        expected_message = CTIMessageFormatter.ipbxcommand_error('service_unavailable')
        connection.send_message.assert_called_once_with(expected_message)

    def test_call_destination_url(self):
        number = '1234'
        url = 'exten:xivo/{0}'.format(number)

        with patch.object(self.manager, 'call_exten') as call:
            self.manager.call_destination(s.connection, s.auth_token, s.user_id, url)
        call.assert_called_once_with(s.connection, s.auth_token, s.user_id, number)

    def test_call_destination_exten(self):
        number = '1234'

        with patch.object(self.manager, 'call_exten') as call:
            self.manager.call_destination(s.connection, s.auth_token, s.user_id, number)
        call.assert_called_once_with(s.connection, s.auth_token, s.user_id, number)

    def test_call_destination_caller_id(self):
        number = '1234'
        caller_id = '"Alice Smith" <{}>'.format(number)

        with patch.object(self.manager, 'call_exten') as call:
            self.manager.call_destination(s.connection, s.auth_token, s.user_id, caller_id)
        call.assert_called_once_with(s.connection, s.auth_token, s.user_id, number)


class TestCallManager(_BaseTest):

    def test_answer_next_ringing_call(self):
        self.manager._get_answer_on_sip_ringing_fn = Mock(return_value=s.fn)

        self.manager.answer_next_ringing_call(self._connection, s.interface)

        self._ami_cb_handler.register_callback.assert_called_once_with(
            self.manager._answer_trigering_event, s.fn)


class TestGetAnswerOnSIPRinging(_BaseTest):

    def test_that_ringing_on_the_good_hint_unregisters_the_callback(self):
        fn = self.manager._get_answer_on_sip_ringing_fn(self._connection, 'SIP/bcde')

        fn({
            'Peer': 'SIP/bcde',
        })

        self._ami_cb_handler.unregister_callback.assert_called_once_with(
            self.manager._answer_trigering_event, fn)
        self._connection.answer_cb.assert_called_once_with()

    def test_that_ringing_on_the_wrong_hint_unregisters_the_callback(self):
        fn = self.manager._get_answer_on_sip_ringing_fn(self._connection, 'SIP/bcde')

        fn({
            'Peer': 'SIP/bad',
        })

        self._assert_nothing_was_called()

    def _assert_nothing_was_called(self):
        assert_that(self._ami_cb_handler.unregister_callback.call_count, equal_to(0))
        assert_that(self._connection.answer_cb.call_count, equal_to(0))
