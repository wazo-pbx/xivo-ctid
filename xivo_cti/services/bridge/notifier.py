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

from xivo_cti.services.bridge.event import BridgeEvent


class BridgeNotifier(object):

    def __init__(self, call_form_dispatch_filter, call_receiver, current_call_manager, innerdata):
        self._call_form_dispatch_filter = call_form_dispatch_filter
        self._call_receiver = call_receiver
        self._current_call_manager = current_call_manager
        self._innerdata = innerdata

    # package private method
    def _on_bridge_enter(self, bridge, channel, linked):
        bridge_event = BridgeEvent(bridge, channel)
        if linked:
            self._innerdata.handle_bridge_link(bridge_event)
            self._call_form_dispatch_filter.handle_bridge_link(bridge_event)
            self._call_receiver.handle_bridge_link(bridge_event)
            self._current_call_manager.handle_bridge_link(bridge_event)

    # package private method
    def _on_bridge_leave(self, bridge, channel, unlinked):
        bridge_event = BridgeEvent(bridge, channel)
        if unlinked:
            self._call_receiver.handle_bridge_unlink(bridge_event)
