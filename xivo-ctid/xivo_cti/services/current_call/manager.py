# -*- coding: utf-8 -*-

# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall'
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import logging
from xivo_dao import user_dao
from xivo_cti import dao
from pprint import pprint


logger = logging.getLogger(__name__)


def state_debug(method):
    def wrapper(self, *args, **kwargs):
        res = method(self, *args, **kwargs)
        logger.debug('---- Internal state ----')
        pprint(self._calls_per_line)
        return res
    return wrapper


class CurrentCallManager(object):

    _SWITCHBOARD_HOLD_QUEUE = '__switchboard_hold'

    def __init__(self, current_call_notifier, current_call_formatter, ami_class, scheduler, device_manager):
        self._calls_per_line = {}
        self._current_call_notifier = current_call_notifier
        current_call_formatter._current_call_manager = self
        self.ami = ami_class
        self.scheduler = scheduler
        self.device_manager = device_manager

    @state_debug
    def bridge_channels(self, channel_1, channel_2):
        line_1 = self._identity_from_channel(channel_1)
        line_2 = self._identity_from_channel(channel_2)

        if line_1 not in self._calls_per_line:
            self._calls_per_line[line_1] = [
                {'channel': channel_2,
                 'lines_channel': channel_1,
                 'bridge_time': time.time(),
                 'on_hold': False}
            ]
            self._current_call_notifier.publish_current_call(line_1)

        if line_2 not in self._calls_per_line:
            self._calls_per_line[line_2] = [
                {'channel': channel_1,
                 'lines_channel': channel_2,
                 'bridge_time': time.time(),
                 'on_hold': False}
            ]
            self._current_call_notifier.publish_current_call(line_2)

    def schedule_answer(self, user_id, delay):
        device_id = user_dao.get_device_id(user_id)
        self.scheduler.schedule(delay, self.device_manager.answer, device_id)

    def masquerade(self, old, new):
        old_2 = self._local_channel_peer(old)
        line_from_old = self._identity_from_channel(old)
        new_2 = self._calls_per_line[line_from_old][0]['channel']

        self._execute_masquerade(old, new)
        self._execute_masquerade(old_2, new_2)

        line_from_new = self._identity_from_channel(new)
        self._current_call_notifier.publish_current_call(line_from_new)

        line_from_new_2 = self._identity_from_channel(new_2)
        self._current_call_notifier.publish_current_call(line_from_new_2)

    def _execute_masquerade(self, old, new):
        self._remove_calls_with_line_channel(old)
        self._substitute_calls_channel(old, new)

    def _substitute_calls_channel(self, old, new):
        while True:
            line, position = self._find_line_and_position(old, 'channel')
            if not line:
                break
            self._calls_per_line[line][position]['channel'] = new

    def _remove_calls_with_line_channel(self, channel):
        while True:
            line, position = self._find_line_and_position(channel, 'lines_channel')
            if not line:
                break
            self._calls_per_line[line].pop(position)

            if not self._calls_per_line[line]:
                self._calls_per_line.pop(line)

    def _find_line_and_position(self, channel, field='channel'):
        for line, calls in self._calls_per_line.iteritems():
            for index, call in enumerate(calls):
                if call[field] == channel:
                    return line, index
        return None, None

    @state_debug
    def end_call(self, channel):
        to_remove = []
        for line, calls in self._calls_per_line.iteritems():
            for call in calls:
                if call['channel'] == channel or call['lines_channel'] == channel:
                    to_remove.append((line, call['channel']))

        for line, channel in to_remove:
            self._remove_peer_channel(line, channel)

        for line in set([line for line, _ in to_remove]):
            self._current_call_notifier.publish_current_call(line)

    @state_debug
    def set_transfer_channel(self, channel, transfer_channel):
        line = self._identity_from_channel(channel)

        if line not in self._calls_per_line:
            return

        for call in self._calls_per_line[line]:
            if call['lines_channel'] != channel:
                continue
            call['transfer_channel'] = transfer_channel

    def _remove_peer_channel(self, line, peer_channel):
        to_be_removed = []

        for position, call_status in enumerate(self._calls_per_line[line]):
            if call_status['channel'] != peer_channel:
                continue
            to_be_removed.append(position)

        for position in to_be_removed:
            self._calls_per_line[line].pop(position)

        if not self._calls_per_line[line]:
            self._calls_per_line.pop(line)

    @state_debug
    def hold_channel(self, holded_channel):
        self._change_hold_status(holded_channel, True)

    @state_debug
    def unhold_channel(self, unholded_channel):
        self._change_hold_status(unholded_channel, False)

    def get_line_calls(self, line_identity):
        return self._calls_per_line.get(line_identity, [])

    def hangup(self, user_id):
        try:
            current_call_channel = self._get_current_call_channel(user_id)
        except LookupError:
            logger.warning('User %s tried to hangup but has no line', user_id)
        else:
            self._hangup_channel(current_call_channel['channel'])

    def complete_transfer(self, user_id):
        try:
            current_call_channel = self._get_current_call_channel(user_id)
        except LookupError:
            logger.warning('User %s tried to complete a transfer but has no line', user_id)
        else:
            self._hangup_channel(current_call_channel['lines_channel'])

    def cancel_transfer(self, user_id):
        try:
            current_call_channel = self._get_current_call_channel(user_id)
        except LookupError:
            logger.warning('User %s tried to cancel a transfer but has no line', user_id)
        else:
            transfer_channel = current_call_channel['transfer_channel']
            transfered_channel = self._local_channel_peer(transfer_channel)
            self._hangup_channel(transfered_channel)

    def attended_transfer(self, user_id, number):
        logger.debug('Transfering %s peer to %s', user_id, number)
        try:
            current_call_channel = self._get_current_call_channel(user_id)
            user_context = dao.user.get_context(user_id)
        except LookupError:
            logger.warning('User %s tried to transfer but has no line or no context', user_id)
        else:
            logger.debug('Sending atxfer: %s %s %s', current_call_channel['lines_channel'], number, user_context)
            self.ami.sendcommand(
                'Atxfer', [
                    ('Channel', current_call_channel['lines_channel']),
                    ('Exten', number),
                    ('Context', user_context),
                    ('Priority', '1')
                ]
            )

    def switchboard_hold(self, user_id):
        try:
            current_call_channel = self._get_current_call_channel(user_id)
            hold_queue_number, hold_queue_ctx = dao.queue.get_number_context_from_name(self._SWITCHBOARD_HOLD_QUEUE)
        except LookupError:
            logger.warning('User %s tried to put his current call on switchboard hold but failed' % user_id)
        else:
            self.ami.transfer(current_call_channel['channel'], hold_queue_number, hold_queue_ctx)

    def switchboard_unhold(self, user_id, action_id):
        try:
            user_line = user_dao.get_line_identity(user_id).lower()
            channel = dao.channel.get_channel_from_unique_id(action_id)
            cid_name, cid_number = dao.channel.get_caller_id_name_number(channel)
        except LookupError:
            raise LookupError('Missing information to complete switchboard unhold on channel %s' % action_id)
        else:
            bridge_option = '%s,Tx' % channel
            self.ami.sendcommand(
                'Originate',
                [('Channel', user_line),
                 ('Application', 'Bridge'),
                 ('Data', bridge_option),
                 ('CallerID', '"%s" <%s>' % (cid_name, cid_number)),
                 ('Async', 'true')]
            )
            self.schedule_answer(user_id, 0.25)

    def _get_current_call_channel(self, user_id):
        try:
            line = user_dao.get_line_identity(user_id).lower()
        except LookupError:
            raise LookupError('User %s has no line' % user_id)
        else:
            calls = self._calls_per_line.get(line, [])
            ongoing_calls = [call for call in calls if call['on_hold'] is False]
            if not ongoing_calls:
                raise LookupError('User %s has no ongoing calls' % user_id)
            return ongoing_calls[0]

    def _change_hold_status(self, channel, new_status):
        line = self._identity_from_channel(channel)
        peer_lines = [self._identity_from_channel(c['channel']) for c in self._calls_per_line[line]]
        for peer_line in peer_lines:
            for call in self._calls_per_line[peer_line]:
                if line not in call['channel'].lower():
                    continue
                call['on_hold'] = new_status
                self._current_call_notifier.publish_current_call(peer_line)

    def _hangup_channel(self, channel):
        self.ami.sendcommand('Hangup', [('Channel', channel)])

    def _local_channel_peer(self, local_channel):
        channel_order = local_channel[-1]
        peer_channel_order = u'1' if channel_order == u'2' else u'2'
        return local_channel[:-1] + peer_channel_order

    @staticmethod
    def _identity_from_channel(channel):
        last_dash = channel.rfind('-')
        if channel.startswith('Local/'):
            end = channel[-2:]
        else:
            end = ''
        return channel[:last_dash].lower() + end
