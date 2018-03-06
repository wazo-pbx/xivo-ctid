# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_cti.services.bridge.event import BridgeEvent

logger = logging.getLogger(__name__)


class BridgeNotifier(object):

    def __init__(self, call_form_dispatch_filter, call_receiver, current_call_manager):
        self._callbacks_bridge_link = [
            call_form_dispatch_filter.handle_bridge_link,
            call_receiver.handle_bridge_link,
            current_call_manager.handle_bridge_link,
        ]
        self._callbacks_bridge_unlink = [
            call_receiver.handle_bridge_unlink,
        ]

    # package private method
    def _on_bridge_enter(self, bridge, channel, linked):
        bridge_event = BridgeEvent(bridge, channel)
        if linked:
            self._call_callbacks(self._callbacks_bridge_link, bridge_event)

    # package private method
    def _on_bridge_leave(self, bridge, channel, unlinked):
        bridge_event = BridgeEvent(bridge, channel)
        if unlinked:
            self._call_callbacks(self._callbacks_bridge_unlink, bridge_event)

    def _call_callbacks(self, callbacks, bridge_event):
        for callback in callbacks:
            try:
                callback(bridge_event)
            except Exception:
                logger.exception('error while calling bridge notifier callback')
