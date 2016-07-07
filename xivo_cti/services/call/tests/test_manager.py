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
from hamcrest import assert_that, calling, equal_to, raises
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
        client_factory = self.manager._new_ctid_ng_client = Mock()
        self.ctid_ng_client = client_factory.return_value


class TestCalls(_BaseTest):

    def test_hangup_calls_async_hangup(self):
        with synchronize(self._runner):
            with patch.object(self.manager, '_async_hangup') as async_hangup:
                self.manager.hangup(s.connection, s.auth_token, s.user_uuid)

        async_hangup.assert_called_once_with(s.connection, self.ctid_ng_client, s.user_uuid)

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

    def test_on_hangup_exception_401(self):
        connection = Mock()
        exception = exceptions.HTTPError(response=Mock(status_code=401))

        self.manager._on_hangup_exception(connection, s.user_uuid, exception)

        expected_message = CTIMessageFormatter.ipbxcommand_error('hangup_unauthorized')
        connection.send_message.assert_called_once_with(expected_message)

    def test_on_hangup_exception_when_ctid_ng_is_down(self):
        connection = Mock()
        exception = exceptions.ConnectionError()

        self.manager._on_hangup_exception(connection, s.user_uuid, exception)

        expected_message = CTIMessageFormatter.ipbxcommand_error('service_unavailable')
        connection.send_message.assert_called_once_with(expected_message)

    def test_on_hangup_exception_when_xivo_auth_is_down(self):
        connection = Mock()
        exception = exceptions.HTTPError(response=Mock(status_code=503))

        self.manager._on_hangup_exception(connection, s.user_uuid, exception)

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


class TestTransfers(_BaseTest):

    def test_transfer_attended(self):
        with patch.object(self.manager, '_transfer') as transfer:
            self.manager.transfer_attended(s.auth_token, s.user_id, s.user_uuid, s.number)

        transfer.assert_called_once_with(s.auth_token, s.user_id, s.user_uuid, s.number, 'attended')

    def test_transfer_attended_exceptions(self):
        exception = Exception()

        with patch.object(self.manager, '_transfer', Mock(side_effect=exception)):
            with patch.object(self.manager, '_on_transfer_exception') as on_exception:
                self.manager.transfer_attended(s.auth_token, s.user_id, s.user_uuid, s.number)

        on_exception.assert_called_once_with(s.user_uuid, s.number, exception)

    def test_transfer_blind(self):
        with patch.object(self.manager, '_transfer') as transfer:
            self.manager.transfer_blind(s.auth_token, s.user_id, s.user_uuid, s.number)

        transfer.assert_called_once_with(s.auth_token, s.user_id, s.user_uuid, s.number, 'blind')

    def test_transfer_blind_exceptions(self):
        exception = Exception()

        with patch.object(self.manager, '_transfer', Mock(side_effect=exception)):
            with patch.object(self.manager, '_on_transfer_exception') as on_exception:
                self.manager.transfer_blind(s.auth_token, s.user_id, s.user_uuid, s.number)

        on_exception.assert_called_once_with(s.user_uuid, s.number, exception)

    def test_transfer_attended_to_voicemail(self):
        with patch.object(self.manager, '_transfer_to_voicemail') as transfer_to_vm:
            self.manager.transfer_attended_to_voicemail(s.auth_token, s.user_uuid, s.voicemail_number)

        transfer_to_vm.assert_called_once_with(s.auth_token, s.user_uuid, s.voicemail_number, 'attended')

    def test_transfer_attended_to_voicemail_exceptions(self):
        exception = Exception()

        with patch.object(self.manager, '_transfer_to_voicemail', Mock(side_effect=exception)):
            with patch.object(self.manager, '_on_transfer_exception') as on_exception:
                self.manager.transfer_attended_to_voicemail(s.auth_token, s.user_uuid, s.vm_number)

        on_exception.assert_called_once_with(s.user_uuid, None, exception)

    def test_transfer_blind_to_voicemail(self):
        with patch.object(self.manager, '_transfer_to_voicemail') as transfer_to_vm:
            self.manager.transfer_blind_to_voicemail(s.auth_token, s.user_uuid, s.voicemail_number)

        transfer_to_vm.assert_called_once_with(s.auth_token, s.user_uuid, s.voicemail_number, 'blind')

    def test_transfer_blind_to_voicemail_exceptions(self):
        exception = Exception()

        with patch.object(self.manager, '_transfer_to_voicemail', Mock(side_effect=exception)):
            with patch.object(self.manager, '_on_transfer_exception') as on_exception:
                self.manager.transfer_blind_to_voicemail(s.auth_token, s.user_uuid, s.vm_number)

        on_exception.assert_called_once_with(s.user_uuid, None, exception)

    def test_transfer_does_nothing_when_no_active_call(self):
        with patch.object(self.manager, '_get_active_call', Mock(return_value=None)):
            self.manager._transfer(s.auth_token, s.user_id, s.user_uuid, s.exten, s.flow)

        assert_that(self.ctid_ng_client.transfers.make_transfer_from_user.call_count, equal_to(0))

    def test_transfer_will_transfer_to_the_active_call(self):
        with patch.object(self.manager, '_get_active_call', Mock(return_value={'call_id': s.call_id})):
            self.manager._transfer(s.auth_token, s.user_id, s.user_uuid, s.exten, s.flow)

        self.ctid_ng_client.transfers.make_transfer_from_user.assert_called_once_with(
            exten=s.exten, initiator=s.call_id, flow=s.flow)

    def test_that_exceptions_are_not_catched_in_transfer(self):
        with patch.object(self.manager, '_get_active_call', Mock(side_effect=Exception)):
            assert_that(calling(self.manager._transfer)
                        .with_args(s.auth_token, s.user_id, s.user_uuid, s.exten, s.flow),
                        raises(Exception))

        self.ctid_ng_client.transfers.make_transfer_from_user.side_effect = Exception
        with patch.object(self.manager, '_get_active_call', Mock(return_value={'call_id': s.call_id})):
            assert_that(calling(self.manager._transfer)
                        .with_args(s.auth_token, s.user_id, s.user_uuid, s.exten, s.flow),
                        raises(Exception))

    def test_transfer_cancel(self):
        transfers = {'items': [{'id': s.transfer_id, 'flow': 'attended'}]}
        self.ctid_ng_client.transfers.list_transfers_from_user.return_value = transfers

        self.manager.transfer_cancel(s.auth_token, s.user_uuid)

        self.ctid_ng_client.transfers.cancel_transfer.assert_called_once_with(s.transfer_id)

    def test_cancel_transfer_no_transfer(self):
        transfers = {'items': []}
        self.ctid_ng_client.transfers.list_transfers_from_user.return_value = transfers

        self.manager.transfer_cancel(s.auth_token, s.user_uuid)

        assert_that(self.ctid_ng_client.transfers.cancel_transfer.call_count, equal_to(0))

    def test_transfer_complete(self):
        transfers = {'items': [{'id': s.transfer_id, 'flow': 'attended'}]}
        self.ctid_ng_client.transfers.list_transfers_from_user.return_value = transfers

        self.manager.transfer_complete(s.auth_token, s.user_uuid)

        self.ctid_ng_client.transfers.complete_transfer_from_user.assert_called_once_with(s.transfer_id)

    def test_transfer_complete_no_transfer(self):
        transfers = {'items': []}
        self.ctid_ng_client.transfers.list_transfers_from_user.return_value = transfers

        self.manager.transfer_complete(s.auth_token, s.user_uuid)

        assert_that(self.ctid_ng_client.transfers.complete_transfer_from_user.call_count, equal_to(0))

    def test_that_exceptions_are_not_catched_in_transfer_to_voicemail(self):
        with patch.object(self.manager, '_get_active_call', Mock(side_effect=Exception)):
            assert_that(calling(self.manager._transfer)
                        .with_args(s.auth_token, s.user_id, s.user_uuid, s.exten, s.flow),
                        raises(Exception))

        self.ctid_ng_client.transfers.make_transfer.side_effect = Exception
        with patch.object(self.manager, '_get_active_call', Mock(return_value={'call_id': s.call_id})):
            assert_that(calling(self.manager._transfer_to_voicemail)
                        .with_args(s.auth_token, s.user_id, s.user_uuid, s.exten, s.flow),
                        raises(Exception))


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
