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

from xivo_cti.services.bridge.event import BridgeEvent

logger = logging.getLogger(__name__)


class BridgeNotifier(object):

    def __init__(self, call_form_dispatch_filter, call_receiver, current_call_manager, innerdata):
        self._callbacks_bridge_link = [
            innerdata.handle_bridge_link,
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
