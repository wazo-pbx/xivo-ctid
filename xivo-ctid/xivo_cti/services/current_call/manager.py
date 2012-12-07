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

from xivo_cti.dao import userfeaturesdao

logger = logging.getLogger(__name__)


class CurrentCallManager(object):

    def __init__(self, current_call_notifier, current_call_formatter):
        self._lines = {}
        self._current_call_notifier = current_call_notifier
        current_call_formatter._current_call_manager = self
        self.ami_class = None

    def bridge_channels(self, channel_1, channel_2):
        line_1 = self._identity_from_channel(channel_1)
        line_2 = self._identity_from_channel(channel_2)

        if line_1 not in self._lines:
            self._lines[line_1] = [
                {'channel': channel_2,
                 'lines_channel': channel_1,
                 'bridge_time': time.time(),
                 'on_hold': False}
            ]
            self._current_call_notifier.publish_current_call(line_1)

        if line_2 not in self._lines:
            self._lines[line_2] = [
                {'channel': channel_1,
                 'lines_channel': channel_2,
                 'bridge_time': time.time(),
                 'on_hold': False}
            ]
            self._current_call_notifier.publish_current_call(line_2)

    def masquerade(self, original, clone):
        line, position = self._find_line_and_position(original)
        if not line:
            return
        cloned_call = self._lines[line][position]
        cloned_call['channel'] = clone
        self._lines[line][position] = cloned_call
        peers_call = {
            'channel': cloned_call['lines_channel'],
            'lines_channel': clone,
            'bridge_time': cloned_call['bridge_time'],
            'on_hold': cloned_call['on_hold']
        }
        peers_line = self._identity_from_channel(clone)
        if peers_line in self._lines:
            self._lines[peers_line].append(peers_call)
        else:
            self._lines[peers_line] = [peers_call]

        self.end_call(original)

        self._current_call_notifier.publish_current_call(line)
        self._current_call_notifier.publish_current_call(peers_line)

    def _find_line_and_position(self, channel):
        for line, calls in self._lines.iteritems():
            for index, call in enumerate(calls):
                if call['channel'] == channel:
                    return line, index
        return None, None

    def end_call(self, channel):
        to_remove = []
        for line, calls in self._lines.iteritems():
            for call in calls:
                if call['channel'] == channel or call['lines_channel'] == channel:
                    to_remove.append((line, call['channel']))

        for line, channel in to_remove:
            self._remove_peer_channel(line, channel)

        for line in set([line for line, _ in to_remove]):
            self._current_call_notifier.publish_current_call(line)

    def _remove_peer_channel(self, line, peer_channel):
        to_be_removed = []

        for position, call_status in enumerate(self._lines[line]):
            if call_status['channel'] != peer_channel:
                continue
            to_be_removed.append(position)

        for position in to_be_removed:
            self._lines[line].pop(position)

        if not self._lines[line]:
            self._lines.pop(line)

    def hold_channel(self, holded_channel):
        self._change_hold_status(holded_channel, True)

    def unhold_channel(self, unholded_channel):
        self._change_hold_status(unholded_channel, False)

    def get_line_calls(self, line_identity):
        return self._lines.get(line_identity, [])

    def hangup(self, user_id):
        try:
            line = userfeaturesdao.get_line_identity(user_id).lower()
        except LookupError:
            logger.warning('User %s tried to hangup but has no line', user_id)
        else:
            calls = self._lines.get(line, [])
            ongoing_calls = [call['lines_channel'] for call in calls if call['on_hold'] is False]
            if not ongoing_calls:
                logger.warning('User %s tried to hangup with no tracked calls', user_id)
            else:
                self.ami_class.sendcommand('hangup', ongoing_calls)

    def _change_hold_status(self, channel, new_status):
        line = self._identity_from_channel(channel)
        peer_lines = [self._identity_from_channel(c['channel']) for c in self._lines[line]]
        for peer_line in peer_lines:
            for call in self._lines[peer_line]:
                if line not in call['channel'].lower():
                    continue
                call['on_hold'] = new_status
                self._current_call_notifier.publish_current_call(peer_line)

    @staticmethod
    def _identity_from_channel(channel):
        last_dash = channel.rfind('-')
        return channel[:last_dash].lower()
