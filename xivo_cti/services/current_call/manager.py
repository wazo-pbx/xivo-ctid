# -*- coding: utf-8 -*-
# Copyright 2007-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import time
import logging

from xivo import caller_id
from xivo.asterisk.line_identity import identity_from_channel
from xivo_bus import Marshaler
from xivo_bus.resources.calls.transfer import AnswerTransferEvent, CancelTransferEvent
from xivo_dao import user_line_dao
from xivo_dao.helpers.db_utils import session_scope

from xivo_cti import dao
from xivo_cti.bus_listener import bus_listener_thread, ack_bus_message

logger = logging.getLogger(__name__)

PEER_CHANNEL = 'peer_channel'
LINE_CHANNEL = 'line_channel'
BRIDGE_TIME = 'bridge_time'
ON_HOLD = 'on_hold'
TRANSFER_CHANNEL = 'transfer_channel'


class CurrentCallManager(object):

    def __init__(self, current_call_notifier, current_call_formatter,
                 ami_class, device_manager, call_manager, call_storage,
                 bus_listener, task_queue, call_pickup_tracker):
        self._calls_per_line = {}
        self._unanswered_transfers = {}
        self._current_call_notifier = current_call_notifier
        current_call_formatter._current_call_manager = self
        self.ami = ami_class
        self.device_manager = device_manager
        self._call_manager = call_manager
        self._call_storage = call_storage
        self._bus_listener = bus_listener
        self._task_queue = task_queue
        self._bus_listener.add_callback(AnswerTransferEvent.routing_key, self._on_bus_transfer_answered)
        self._tracker = call_pickup_tracker

    @bus_listener_thread
    @ack_bus_message
    def _on_bus_transfer_answered(self, body):
        event_name = body.get('name')
        if event_name == 'transfer_answered':
            event = Marshaler.unmarshal_message(body, AnswerTransferEvent)
            if event.transfer['flow'] == 'attended':
                self._task_queue.put(self._transfer_answered,
                                     event.transfer['initiator_uuid'])
        elif event_name == 'transfer_cancelled':
            event = Marshaler.unmarshal_message(body, CancelTransferEvent)
            if event.transfer['flow'] == 'attended':
                self._task_queue.put(self._transfer_cancelled,
                                     event.transfer['initiator_uuid'])

    def _transfer_answered(self, user_uuid):
        logger.debug('bus transfer_answered received: user uuid: %s', user_uuid)
        if user_uuid:
            line = dao.user.get_line_identity(user_uuid)
            self._current_call_notifier.attended_transfer_answered(line)

    def _transfer_cancelled(self, user_uuid):
        logger.debug('bus transfer_cancelled received: user uuid: %s', user_uuid)
        if user_uuid:
            line = dao.user.get_line_identity(user_uuid)
            self._current_call_notifier.attended_transfer_cancelled(line)

    def handle_bridge_link(self, bridge_event):
        channel_1, channel_2 = bridge_event.bridge.channels
        self._bridge_channels(channel_1.channel, channel_2.channel)

    def _bridge_channels(self, channel_1, channel_2):
        self._bridge_channels_oriented(channel_1, channel_2)
        self._bridge_channels_oriented(channel_2, channel_1)

    def _bridge_channels_oriented(self, channel, other_channel):
        line = identity_from_channel(channel)
        if line not in self._calls_per_line:
            self._calls_per_line[line] = [
                {PEER_CHANNEL: other_channel,
                 LINE_CHANNEL: channel,
                 BRIDGE_TIME: time.time(),
                 ON_HOLD: False}
            ]
            self._current_call_notifier.publish_current_call(line)

        self._check_attended_transfer_target_answered(channel)

    def _check_attended_transfer_target_answered(self, transfer_channel):
        transferer_channel = self._unanswered_transfers.get(transfer_channel)
        if not transferer_channel:
            return

        line = identity_from_channel(transferer_channel)
        line_calls = self._calls_per_line.get(line)
        if not line_calls:
            return

        for line_call in line_calls:
            if line_call[LINE_CHANNEL] == transferer_channel:
                self._current_call_notifier.attended_transfer_answered(line)
                del self._unanswered_transfers[transfer_channel]
                break

    def on_local_optimization(self, local_one_channel, local_two_channel):
        local_one_call = self._find_call(local_one_channel)
        if not local_one_call:
            logger.info('local optimization: no call for channel %s', local_one_channel)
            return
        local_two_call = self._find_call(local_two_channel)
        if not local_two_call:
            logger.info('local optimization: no call for channel %s', local_two_channel)
            return

        source_call = self._find_call(local_one_call[PEER_CHANNEL])
        if source_call:
            source_call[PEER_CHANNEL] = local_two_call[PEER_CHANNEL]
        dest_call = self._find_call(local_two_call[PEER_CHANNEL])
        if dest_call:
            dest_call[PEER_CHANNEL] = local_one_call[PEER_CHANNEL]

        self._remove_call(local_one_channel)
        self._remove_call(local_two_channel)

    def _find_call(self, channel):
        line = identity_from_channel(channel)
        calls = self._calls_per_line.get(line)
        if not calls:
            return None

        for call in calls:
            if call[LINE_CHANNEL] == channel:
                return call
        return None

    def _remove_call(self, channel):
        line = identity_from_channel(channel)
        calls = self._calls_per_line[line]
        new_calls = [call for call in calls if call[LINE_CHANNEL] != channel]
        if new_calls:
            self._calls_per_line[line] = new_calls
        else:
            del self._calls_per_line[line]

    def _find_line_and_position(self, channel, field=PEER_CHANNEL):
        for line, calls in self._calls_per_line.iteritems():
            for index, call in enumerate(calls):
                if field in call and call[field] == channel:
                    yield line, index

    def end_call(self, channel):
        to_remove = []
        for line, calls in self._calls_per_line.iteritems():
            for call in calls:
                if call[PEER_CHANNEL] == channel or call[LINE_CHANNEL] == channel:
                    to_remove.append((line, call[PEER_CHANNEL]))

        self._unanswered_transfers.pop(channel, None)

        for line, channel in to_remove:
            self._remove_peer_channel(line, channel)

        for line in set([line for line, _ in to_remove]):
            self._current_call_notifier.publish_current_call(line)

    def remove_transfer_channel(self, channel):
        for line, position in self._find_line_and_position(channel, TRANSFER_CHANNEL):
            self._calls_per_line[line][position].pop(TRANSFER_CHANNEL)
            self._current_call_notifier.publish_current_call(line)

    def set_transfer_channel(self, channel, transfer_channel):
        if transfer_channel.endswith(';1'):
            return

        line = identity_from_channel(channel)
        if line not in self._calls_per_line:
            return

        for call in self._calls_per_line[line]:
            if call[LINE_CHANNEL] != channel:
                continue
            call[TRANSFER_CHANNEL] = transfer_channel

        self._unanswered_transfers[transfer_channel] = channel

    def _remove_peer_channel(self, line, peer_channel):
        to_be_removed = []

        for position, call_status in enumerate(self._calls_per_line[line]):
            if call_status[PEER_CHANNEL] != peer_channel:
                continue
            to_be_removed.append(position)

        for position in to_be_removed:
            self._calls_per_line[line].pop(position)

        if not self._calls_per_line[line]:
            self._calls_per_line.pop(line)

    def hold_channel(self, holded_channel):
        self._change_hold_status(holded_channel, True)

    def unhold_channel(self, unholded_channel):
        self._change_hold_status(unholded_channel, False)

    def get_line_calls(self, line_identity):
        return self._calls_per_line.get(line_identity, [])

    def switchboard_hold(self, connection, auth_token, user_id, user_uuid, on_hold_queue):
        try:
            hold_queue_number, hold_queue_ctx = dao.queue.get_number_context_from_name(on_hold_queue)
            self._call_manager.transfer_blind(connection, auth_token, user_id, user_uuid, hold_queue_number)
        except LookupError as e:
            logger.info('switchboard_hold: %s', e)
            logger.exception(e)

    def switchboard_retrieve_waiting_call(self, user_id, unique_id, client_connection):
        logger.info('Switchboard %s retrieving channel %s', user_id, unique_id)
        try:
            # The mark should be removed if the operation does not complete
            self._tracker.mark(unique_id)
        except Exception:
            logger.info('the call %s is already being answered by someone', unique_id)
            return

        if self._get_ongoing_calls(user_id):
            logger.info('Switchboard %s may not retrieve channel %s because he has ongoing calls', user_id, unique_id)
            self._tracker.unmark(unique_id)
            return

        try:
            channel_to_retrieve = dao.channel.get_channel_from_unique_id(unique_id)
        except LookupError:
            logger.warning('Switchboard %s tried to retrieve non-existent channel %s', user_id, unique_id)
            self._tracker.unmark(unique_id)
            return
        try:
            line = dao.user.get_line(user_id)
            line_identity = line['identity'].lower()
            cid_name, cid_num = dao.channel.get_caller_id_name_number(channel_to_retrieve)
            cid_name_src, cid_num_src = self._get_cid_name_and_number_from_line(line)
            ringing_channels = dao.channel.channels_from_identity(line_identity)
        except LookupError:
            self._tracked.unmark(unique_id)
            raise LookupError('Missing information for the switchboard to retrieve channel %s' % unique_id)
        else:
            map(self.ami.hangup_with_cause_answered_elsewhere, ringing_channels)
            self.ami.switchboard_retrieve(line_identity, channel_to_retrieve, cid_name, cid_num, cid_name_src, cid_num_src)
            self._call_manager.answer_next_ringing_call(client_connection, line_identity)

    def _get_cid_name_and_number_from_line(self, line):
        try:
            cid_name = caller_id.extract_displayname(line['callerid'])
            cid_num = caller_id.extract_number(line['callerid'])
        except ValueError:
            cid_name = ''
            cid_num = ''
        return cid_name, cid_num

    def _get_current_call(self, user_id):
        ongoing_calls = self._get_ongoing_calls(user_id)
        if not ongoing_calls:
            raise LookupError('failed to find the current call for user (%s)' % user_id)
        return ongoing_calls[0]

    def _get_context(self, user_id):
        user_context = dao.user.get_context(user_id)
        if not user_context:
            raise LookupError('failed to find the context for user (%s)' % user_id)

        return user_context

    def _get_ongoing_calls(self, user_id):
        try:
            with session_scope():
                line = user_line_dao.get_line_identity_by_user_id(user_id).lower()
        except LookupError:
            raise LookupError('User %s has no line' % user_id)
        else:
            calls = self._calls_per_line.get(line, [])
            ongoing_calls = [call for call in calls if call[ON_HOLD] is False]
            return ongoing_calls

    def _change_hold_status(self, channel, new_status):
        line = identity_from_channel(channel)
        if line not in self._calls_per_line:
            logger.warning('No tracked calls for channel %s to set hold to %s',
                           channel, new_status)
            logger.debug('Lines with tracked calls %s', self._calls_per_line.keys())
            return
        peer_lines = [identity_from_channel(c[PEER_CHANNEL]) for c in self._calls_per_line[line]]
        for peer_line in peer_lines:
            for call in self._calls_per_line[peer_line]:
                if line not in call[PEER_CHANNEL].lower():
                    continue
                call[ON_HOLD] = new_status
                self._current_call_notifier.publish_current_call(peer_line)

    def _local_channel_peer(self, local_channel):
        channel_order = local_channel[-1]
        peer_channel_order = u'1' if channel_order == u'2' else u'2'
        return local_channel[:-1] + peer_channel_order


class CallPickupTracker(object):

    def __init__(self):
        self._marked = set()

    def handle_hangup(self, event):
        unique_id = event['Uniqueid']
        if self.is_marked(unique_id):
            logger.info('removing mark from hung up call %s', unique_id)
            self._unmark(unique_id)

    def mark(self, unique_id):
        logger.info('marking call %s as being picked up', unique_id)
        if self.is_marked(unique_id):
            raise Exception('Already marked')
        self._marked.add(unique_id)

    def unmark(self, unique_id):
        logger.info('marking call %s as being available for pickup', unique_id)
        return self._unmark(unique_id)

    def _unmark(self, unique_id):
        try:
            self._marked.remove(unique_id)
        except KeyError:
            return

    def is_marked(self, unique_id):
        return unique_id in self._marked
