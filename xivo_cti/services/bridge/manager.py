# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
