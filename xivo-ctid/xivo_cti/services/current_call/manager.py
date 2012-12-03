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
# contracted with Avencall. See the LICENSE file at top of the souce tree
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
        self._channels = {}

    def bridge_channels(self, channel_1, channel_2):
        self._channels[channel_1] = [
            {'channel': channel_2,
             'bridge_time': time.time(),
             'on_hold': False}]
        self._channels[channel_2] = [
            {'channel': channel_1,
             'bridge_time': time.time(),
             'on_hold': False}]

    def unbridge_channels(self, channel_1, channel_2):
        self._remove_peer_channel(channel_1, channel_2)
        self._remove_peer_channel(channel_2, channel_1)

    def _remove_peer_channel(self, channel, peer_channel):
        to_be_removed = []

        for position, channel_status in enumerate(self._channels[channel]):
            if channel_status['channel'] != peer_channel:
                continue
            to_be_removed.append(position)

        for position in to_be_removed:
            self._channels[channel].pop(position)

        if not self._channels[channel]:
            self._channels.pop(channel)

    def hold_channel(self, holded_channel):
        self._change_hold_status(holded_channel, True)

    def unhold_channel(self, unholded_channel):
        self._change_hold_status(unholded_channel, False)

    def _change_hold_status(self, holded_channel, new_status):
        peer_channels = [c['channel'] for c in self._channels[holded_channel]]
        for peer_channel in peer_channels:
            for channel in self._channels[peer_channel]:
                if channel['channel'] != holded_channel:
                    continue
                channel['on_hold'] = new_status
