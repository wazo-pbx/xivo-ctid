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


class CurrentCallManager(object):

    def __init__(self):
        self._lines = {}

    def bridge_channels(self, channel_1, channel_2):
        line_1 = self._identity_from_channel(channel_1)
        line_2 = self._identity_from_channel(channel_2)
        self._lines[line_1] = [
            {'channel': channel_2,
             'bridge_time': time.time(),
             'on_hold': False}]
        self._lines[line_2] = [
            {'channel': channel_1,
             'bridge_time': time.time(),
             'on_hold': False}]

    def unbridge_channels(self, channel_1, channel_2):
        line_1 = self._identity_from_channel(channel_1)
        line_2 = self._identity_from_channel(channel_2)
        self._remove_peer_channel(line_1, channel_2)
        self._remove_peer_channel(line_2, channel_1)

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
        line = self._identity_from_channel(holded_channel)
        self._change_hold_status(line, True)

    def unhold_channel(self, unholded_channel):
        line = self._identity_from_channel(unholded_channel)
        self._change_hold_status(line, False)

    def get_line_calls(self, line_identity):
        return self._lines.get(line_identity, [])

    def _change_hold_status(self, line, new_status):
        peer_lines = [self._identity_from_channel(c['channel']) for c in self._lines[line]]
        for peer_line in peer_lines:
            for call in self._lines[peer_line]:
                if line not in call['channel']:
                    continue
                call['on_hold'] = new_status

    @staticmethod
    def _identity_from_channel(channel):
        last_dash = channel.rfind('-')
        return channel[:last_dash]
