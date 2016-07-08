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

import logging

from functools import partial

from requests import ConnectionError, HTTPError

from xivo import caller_id
from xivo_ctid_ng_client import Client as CtidNgClient

from xivo_cti import config, dao
from xivo_cti.async_runner import async_runner_thread
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter
from xivo_cti.model.destination_factory import DestinationFactory

logger = logging.getLogger(__name__)


class _BaseExceptionHandler(object):

    def __init__(self, connection, user_uuid):
        self._connection = connection
        self._user_uuid = user_uuid

    def handle(self, exception):
        logger.info('%s failed to %s: %s', self._user_uuid, self.operation, exception)
        try:
            raise exception
        except HTTPError as e:
            status_code = getattr(getattr(e, 'response', None), 'status_code', None)
            handled = self._handle_http_error(status_code)
            if not handled:
                raise
        except ConnectionError:
            return self._service_unavailable()

    def _handle_http_error(self, status_code):
        if status_code == 401:
            return self._unauthorized()
        elif status_code == 503:
            return self._service_unavailable()
        return False

    def _unauthorized(self):
        error_string = '{}_unauthorized'.format(self.operation)
        return self._send_error(error_string)

    def _service_unavailable(self):
        error_string = 'service_unavailable'
        return self._send_error(error_string)

    def _send_error(self, error_string):
        error_message = CTIMessageFormatter.ipbxcommand_error(error_string)
        self._connection.send_message(error_message)
        return True


class _ExtensionTargettingExceptionHandler(_BaseExceptionHandler):

    def __init__(self, connection, user_id, exten):
        super(_ExtensionTargettingExceptionHandler, self).__init__(connection, user_id)
        self._exten = exten

    def _handle_http_error(self, status_code):
        if status_code == 400:
            return self._invalid_extension()
        else:
            return super(_ExtensionTargettingExceptionHandler, self)._handle_http_error(status_code)

    def _invalid_extension(self):
        error_string = 'unreachable_extension:{}'.format(self._exten)
        return self._send_error(error_string)


class _CallExceptionHandler(_ExtensionTargettingExceptionHandler):
    operation = 'call'


class _HangupExceptionHandler(_BaseExceptionHandler):
    operation = 'hangup'


class _TransferExceptionHandler(_ExtensionTargettingExceptionHandler):
    operation = 'transfer'


class _TransferToVoicemailExceptionHandler(_BaseExceptionHandler):
    operation = 'transfer'


class _TransferCompletionExceptionHandler(_BaseExceptionHandler):
    operation = 'transfer'


class CallManager(object):

    _answer_trigering_event = 'SIPRinging'

    def __init__(self, ami_class, ami_callback_handler, async_runner):
        self._ami = ami_class
        self._ami_cb_handler = ami_callback_handler
        self._runner = async_runner

    def answer_next_ringing_call(self, connection, interface):
        fn = self._get_answer_on_sip_ringing_fn(connection, interface)
        self._ami_cb_handler.register_callback(self._answer_trigering_event, fn)

    def call_destination(self, connection, auth_token, user_id, url_or_exten):
        if DestinationFactory.is_destination_url(url_or_exten):
            exten = DestinationFactory.make_from(url_or_exten).to_exten()
        elif caller_id.is_complete_caller_id(url_or_exten):
            exten = caller_id.extract_number(url_or_exten)
        else:
            exten = url_or_exten

        self.call_exten(connection, auth_token, user_id, exten)

    def call_exten(self, connection, auth_token, user_id, exten):
        logger.info('call_exten: %s is calling %s', user_id, exten)
        client = self._new_ctid_ng_client(auth_token)
        error_handler = _CallExceptionHandler(connection, user_id, exten)
        success_cb = partial(self._on_call_success, connection, user_id)
        self._runner.run(client.calls.make_call_from_user, extension=exten,
                         _on_response=success_cb,
                         _on_error=error_handler.handle)

    def hangup(self, connection, auth_token, user_uuid):
        logger.info('hangup: user %s is hanging up his current call', user_uuid)
        client = self._new_ctid_ng_client(auth_token)
        error_handler = _HangupExceptionHandler(connection, user_uuid)
        self._runner.run(self._async_hangup, connection, client, user_uuid,
                         _on_error=error_handler.handle)

    def transfer_attended(self, connection, auth_token, user_id, user_uuid, number):
        logger.info('transfer_attended: user %s is transfering a call to %s', user_uuid, number)
        error_handler = _TransferExceptionHandler(connection, user_uuid, number)
        self._runner.run(self._transfer, auth_token, user_id, user_uuid, number, 'attended',
                         _on_error=error_handler.handle)

    def transfer_attended_to_voicemail(self, connection, auth_token, user_uuid, voicemail_number):
        logger.info('transfer_attended_to_voicemail: user %s is transfering to voicemail %s', user_uuid, voicemail_number)
        user_context = dao.user.get_context(user_uuid)
        if not user_context:
            logger.info('transfer_attended_to_voicemail: failed to transfer %s is not a member of any context', user_uuid)
            return

        error_handler = _TransferToVoicemailExceptionHandler(connection, user_uuid)
        self._runner.run(self._transfer_to_voicemail, auth_token, user_uuid,
                         voicemail_number, user_context, 'attended',
                         _on_error=error_handler.handle)

    def transfer_blind(self, connection, auth_token, user_id, user_uuid, number):
        logger.info('transfer_blind: user %s is transfering a call to %s', user_uuid, number)
        error_handler = _TransferExceptionHandler(connection, user_uuid, number)
        self._runner.run(self._transfer, auth_token, user_id, user_uuid, number, 'blind',
                         _on_error=error_handler.handle)

    def transfer_blind_to_voicemail(self, connection, auth_token, user_uuid, voicemail_number):
        logger.info('transfer_blind_to_voicemail: user %s is transfering to voicemail %s', user_uuid, voicemail_number)
        user_context = dao.user.get_context(user_uuid)
        if not user_context:
            logger.info('transfer_blind_to_voicemail: failed to transfer %s is not a member of any context', user_uuid)
            return

        error_handler = _TransferToVoicemailExceptionHandler(connection, user_uuid)
        self._runner.run(self._transfer_to_voicemail, auth_token, user_uuid, voicemail_number, user_context, 'blind',
                         _on_error=error_handler.handle)

    def transfer_cancel(self, connection, auth_token, user_uuid):
        logger.info('cancel_transfer: user %s is cancelling a transfer', user_uuid)
        error_handler = _TransferCompletionExceptionHandler(connection, user_uuid)
        self._runner.run(self._transfer_cancel_async, auth_token, user_uuid,
                         _on_error=error_handler.handle)

    @async_runner_thread
    def _transfer_cancel_async(self, auth_token, user_uuid):
        client = self._new_ctid_ng_client(auth_token)
        transfer = self._get_current_transfer(client)
        if transfer:
            return client.transfers.cancel_transfer(transfer['id'])

        logger.info('cancel_transfer: No transfer to cancel for %s', user_uuid)

    def transfer_complete(self, connection, auth_token, user_uuid):
        logger.info('complete_transfer: user %s is completing a transfer', user_uuid)
        error_handler = _TransferCompletionExceptionHandler(connection, user_uuid)
        self._runner.run(self._transfer_complete_async, auth_token, user_uuid,
                         _on_error=error_handler.handle)

    @async_runner_thread
    def _transfer_complete_async(self, auth_token, user_uuid):
        client = self._new_ctid_ng_client(auth_token)
        transfer = self._get_current_transfer(client)
        if transfer:
            return client.transfers.complete_transfer_from_user(transfer['id'])

        logger.info('complete_transfer: No transfer to complete for %s', user_uuid)

    @async_runner_thread
    def _async_hangup(self, connection, client, user_uuid):
        active_call = self._get_active_call(client)
        if not active_call:
            logger.info('hangup: failed to find the active call for user %s', user_uuid)
            return

        return client.calls.hangup_from_user(active_call['call_id'])

    @staticmethod
    @async_runner_thread
    def _get_active_call(client):
        calls = client.calls.list_calls_from_user()
        for call in calls['items']:
            if call['status'] == 'Up' and not call['on_hold']:
                return call

    @staticmethod
    @async_runner_thread
    def _get_current_transfer(client):
        transfers = client.transfers.list_transfers_from_user()
        for transfer in transfers['items']:
            if transfer['flow'] == 'attended':
                return transfer

    def _on_call_success(self, connection, user_id, response):
        interface = dao.user.get_line_identity(user_id)
        if interface:
            self.answer_next_ringing_call(connection, interface)

    def _get_answer_on_sip_ringing_fn(self, connection, interface):
        def answer_if_matching_peer(event):
            if event['Peer'].lower() != interface.lower():
                return

            self._ami_cb_handler.unregister_callback(self._answer_trigering_event,
                                                     answer_if_matching_peer)
            connection.answer_cb()

        return answer_if_matching_peer

    @async_runner_thread
    def _transfer(self, auth_token, user_id, user_uuid, number, flow):
        client = self._new_ctid_ng_client(auth_token)
        active_call = self._get_active_call(client)
        if not active_call:
            logger.info('transfer to %s failed for user %s. No active call', number, user_uuid)
            return

        return client.transfers.make_transfer_from_user(exten=number,
                                                        initiator=active_call['call_id'],
                                                        flow=flow)

    @async_runner_thread
    def _transfer_to_voicemail(self, auth_token, user_uuid, voicemail_number, user_context, flow):
        client = self._new_ctid_ng_client(auth_token)
        active_call = self._get_active_call(client)
        if not active_call:
            logger.info('transfer to voicemail %s failed for user %s. No active call', voicemail_number, user_uuid)
            return

        variables = {'XIVO_BASE_CONTEXT': user_context, 'ARG1': voicemail_number}
        transfer_params = self._make_transfer_param_from_call(active_call, 's', 'vmbox', flow, variables)
        client = self._new_ctid_ng_client(config['auth']['token'])
        return client.transfers.make_transfer(**transfer_params)

    @staticmethod
    @async_runner_thread
    def _make_transfer_param_from_call(call, exten, context, flow=None, variables=None):
        transfered_call_id = call['talking_to'].keys()[0]
        initiator_call_id = call['call_id']
        base_params = {'transferred': transfered_call_id,
                       'initiator': initiator_call_id,
                       'exten': exten,
                       'context': context}

        if flow:
            base_params['flow'] = flow
        if variables:
            base_params['variables'] = variables

        return base_params

    @staticmethod
    @async_runner_thread
    def _new_ctid_ng_client(auth_token):
        return CtidNgClient(token=auth_token, **config['ctid_ng'])
