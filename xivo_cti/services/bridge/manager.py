# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

from xivo_cti.services.bridge.bridge import Bridge

logger = logging.getLogger(__name__)


class BridgeManager(object):

    def __init__(self, bridge_notifier, innerdata):
        self._bridge_notifier = bridge_notifier
        self._innerdata = innerdata
        self._bridges = {}

    # package private method
    def _on_bridge_create(self, bridge_id, bridge_type):
        self._add_bridge(bridge_id, bridge_type)

    # package private method
    def _on_bridge_destroy(self, bridge_id):
        del self._bridges[bridge_id]

    # package private method
    def _on_bridge_enter(self, bridge_id, channel_name):
        bridge = self._bridges[bridge_id]
        channel = self._innerdata.channels[channel_name]

        bridge._add_channel(channel)
        self._bridge_notifier._on_bridge_enter(bridge, channel, bridge.linked())

    # package private method
    def _on_bridge_leave(self, bridge_id, channel_name):
        bridge = self._bridges[bridge_id]
        channel = self._innerdata.channels[channel_name]

        was_linked = bridge.linked()
        bridge._remove_channel(channel)
        unlinked = was_linked and not bridge.linked()
        self._bridge_notifier._on_bridge_leave(bridge, channel, unlinked)

    # package private method
    def _add_bridge(self, bridge_id, bridge_type):
        self._bridges[bridge_id] = Bridge(bridge_id, bridge_type)

    # package private method
    def _add_channel_to_bridge(self, bridge_id, channel_name):
        bridge = self._bridges[bridge_id]
        channel = self._innerdata.channels[channel_name]

        bridge._add_channel(channel)

    # package private method
    def _finish_bridge_initialization(self, bridge_id):
        bridge = self._bridges[bridge_id]
        if bridge.linked():
            channel_1, channel_2 = bridge.channels
            self._innerdata.setpeerchannel(channel_1.channel, channel_2.channel)
            self._innerdata.setpeerchannel(channel_2.channel, channel_1.channel)
