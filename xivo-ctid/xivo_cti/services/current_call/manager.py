# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

import time
import logging
from xivo.asterisk.line_identity import identity_from_channel
from xivo_dao import user_line_dao
from xivo_cti import dao


logger = logging.getLogger(__name__)


PEER_CHANNEL = 'peer_channel'
LINE_CHANNEL = 'line_channel'
BRIDGE_TIME = 'bridge_time'
ON_HOLD = 'on_hold'
TRANSFER_CHANNEL = 'transfer_channel'


class CurrentCallManager(object):

    def __init__(self, current_call_notifier, current_call_formatter, ami_class, scheduler, device_manager):
        self._calls_per_line = {}
        self._current_call_notifier = current_call_notifier
        current_call_formatter._current_call_manager = self
        self.ami = ami_class
        self.scheduler = scheduler
        self.device_manager = device_manager

    def bridge_channels(self, channel_1, channel_2):
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

        line_calls = self._calls_per_line[line]
        if self._attended_transfer_from_line_is_answered(line_calls, other_channel):
            self._current_call_notifier.attended_transfer_answered(line)

    def _attended_transfer_from_line_is_answered(self, line_calls, channel_transferee):
        for line_call in line_calls:
            if TRANSFER_CHANNEL not in line_call:
                continue
            if line_call[TRANSFER_CHANNEL] == channel_transferee:
                return True
        return False

    def schedule_answer(self, answer_fn, delay):
        self.scheduler.schedule(delay, answer_fn)

    def masquerade(self, old, new):
        old_2 = self._local_channel_peer(old)
        line_from_old = identity_from_channel(old)
        if line_from_old not in self._calls_per_line:
            logger.debug('No masquerade done for channel %s %s', old, new)
            return
        new_2 = self._calls_per_line[line_from_old][0][PEER_CHANNEL]

        self._execute_masquerade(old, new)
        self._execute_masquerade(old_2, new_2)

        line_from_new = identity_from_channel(new)
        self._current_call_notifier.publish_current_call(line_from_new)

        line_from_new_2 = identity_from_channel(new_2)
        self._current_call_notifier.publish_current_call(line_from_new_2)

    def _execute_masquerade(self, old, new):
        self._remove_calls_with_line_channel(old)
        self._substitute_calls_channel(old, new)

    def _substitute_calls_channel(self, old, new):
        while True:
            line, position = self._find_line_and_position(old, PEER_CHANNEL)
            if not line:
                break
            self._calls_per_line[line][position][PEER_CHANNEL] = new

    def _remove_calls_with_line_channel(self, channel):
        while True:
            line, position = self._find_line_and_position(channel, LINE_CHANNEL)
            if not line:
                break
            self._calls_per_line[line].pop(position)

            if not self._calls_per_line[line]:
                self._calls_per_line.pop(line)

    def _find_line_and_position(self, channel, field=PEER_CHANNEL):
        for line, calls in self._calls_per_line.iteritems():
            for index, call in enumerate(calls):
                if field in call and call[field] == channel:
                    return line, index
        return None, None

    def end_call(self, channel):
        to_remove = []
        for line, calls in self._calls_per_line.iteritems():
            for call in calls:
                if call[PEER_CHANNEL] == channel or call[LINE_CHANNEL] == channel:
                    to_remove.append((line, call[PEER_CHANNEL]))

        for line, channel in to_remove:
            self._remove_peer_channel(line, channel)

        for line in set([line for line, _ in to_remove]):
            self._current_call_notifier.publish_current_call(line)

    def remove_transfer_channel(self, channel):
        line, position = self._find_line_and_position(channel, TRANSFER_CHANNEL)
        if line:
            self._calls_per_line[line][position].pop(TRANSFER_CHANNEL)

            self._current_call_notifier.publish_current_call(line)

    def set_transfer_channel(self, channel, transfer_channel):
        line = identity_from_channel(channel)

        if line not in self._calls_per_line:
            return

        for call in self._calls_per_line[line]:
            if call[LINE_CHANNEL] != channel:
                continue
            call[TRANSFER_CHANNEL] = transfer_channel

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

    def hangup(self, user_id):
        try:
            current_call = self._get_current_call(user_id)
        except LookupError:
            logger.warning('User %s tried to hangup but has no line', user_id)
        else:
            logger.info('Switchboard %s is hanging up his current call', user_id)
            self.ami.hangup(current_call[PEER_CHANNEL])

    def complete_transfer(self, user_id):
        try:
            current_call = self._get_current_call(user_id)
        except LookupError:
            logger.warning('User %s tried to complete a transfer but has no line', user_id)
        else:
            logger.info('Switchboard %s is completing a transfer', user_id)
            self.ami.hangup(current_call[LINE_CHANNEL])

    def cancel_transfer(self, user_id):
        try:
            current_call = self._get_current_call(user_id)
        except LookupError:
            logger.warning('User %s tried to cancel a transfer but has no line', user_id)
            return

        if TRANSFER_CHANNEL not in current_call:
            return
        transfer_channel = current_call[TRANSFER_CHANNEL]
        transfered_channel = self._local_channel_peer(transfer_channel)
        logger.info('Switchboard %s is cancelling a transfer', user_id)
        self.ami.hangup(transfered_channel)

    def attended_transfer(self, user_id, number):
        try:
            current_call = self._get_current_call(user_id)
            user_context = dao.user.get_context(user_id)
        except LookupError:
            logger.warning('User %s tried to transfer but has no line or no context', user_id)
        else:
            current_channel = current_call[LINE_CHANNEL]
            logger.info('Switchboard %s is atxfering %s to %s@%s',
                        user_id, current_channel, number, user_context)
            self.ami.atxfer(current_channel, number, user_context)

    def direct_transfer(self, user_id, number):
        try:
            current_call = self._get_current_call(user_id)
            user_context = dao.user.get_context(user_id)
        except LookupError:
            logger.warning('User %s tried to transfer but has no line or no context', user_id)
        else:
            peer_channel = current_call[PEER_CHANNEL]
            logger.info('Switchboard %s is transfering %s to %s@%s',
                        user_id, peer_channel, number, user_context)
            self.ami.transfer(peer_channel, number, user_context)

    def switchboard_hold(self, user_id, on_hold_queue):
        try:
            current_call = self._get_current_call(user_id)
            hold_queue_number, hold_queue_ctx = dao.queue.get_number_context_from_name(on_hold_queue)
        except LookupError as e:
            logger.warning('User %s tried to put his current call on switchboard hold but failed' % user_id)
            logger.exception(e)
        else:
            channel_to_hold = current_call[PEER_CHANNEL]
            logger.info('Switchboard %s sending %s on hold', user_id, channel_to_hold)
            self.ami.transfer(channel_to_hold, hold_queue_number, hold_queue_ctx)

    def switchboard_retrieve_waiting_call(self, user_id, unique_id, client_connection):
        logger.info('Switchboard %s retrieving channel %s', user_id, unique_id)

        if self._get_ongoing_calls(user_id):
            logger.info('Switchboard %s may not retrieve channel %s because he has ongoing calls', user_id, unique_id)
            return

        try:
            user_line = user_line_dao.get_line_identity_by_user_id(user_id).lower()
            channel_to_retrieve = dao.channel.get_channel_from_unique_id(unique_id)
            cid_name, cid_num = dao.channel.get_caller_id_name_number(channel_to_retrieve)
            ringing_channels = dao.channel.channels_from_identity(user_line)
        except LookupError:
            raise LookupError('Missing information for the switchboard to retrieve channel %s' % unique_id)
        else:
            map(self.ami.hangup, ringing_channels)
            self.ami.switchboard_retrieve(user_line, channel_to_retrieve, cid_name, cid_num)
            self.schedule_answer(client_connection.answer_cb, 0.25)

    def _get_current_call(self, user_id):
        ongoing_calls = self._get_ongoing_calls(user_id)
        if not ongoing_calls:
            raise LookupError('User %s has no ongoing calls' % user_id)
        return ongoing_calls[0]

    def _get_ongoing_calls(self, user_id):
        try:
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
            logger.warning('No line associated to channel %s to set hold to %s',
                           channel, new_status)
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
