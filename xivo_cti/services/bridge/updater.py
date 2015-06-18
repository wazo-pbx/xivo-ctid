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

import time


class BridgeUpdater(object):
    # TODO handle more bridge events (bridge merge?)

    def __init__(self, bridge_manager, ami_class, innerdata, call_form_dispatch_filter,
                 call_storage, call_receiver, current_call_manager):
        self._ami_class = ami_class
        self._bridge_manager = bridge_manager
        self._call_form_dispatch_filter = call_form_dispatch_filter
        self._call_receiver = call_receiver
        self._call_storage = call_storage
        self._current_call_manager = current_call_manager
        self._innerdata = innerdata

    def on_ami_bridge_create(self, event):
        bridge_id = event['BridgeUniqueid']
        self._bridge_manager._add_bridge(bridge_id)

    def on_ami_bridge_destroy(self, event):
        bridge_id = event['BridgeUniqueid']
        self._bridge_manager._remove_bridge(bridge_id)

    def on_ami_bridge_enter(self, event):
        bridge_id = event['BridgeUniqueid']
        channel_name = event['Channel']
        bridge = self._bridge_manager.get_bridge(bridge_id)
        bridge.channels.append(channel_name)
        self._update_channels(bridge_id)
        self._link_call_receiver(bridge_id)
        self._link_parse_bridge(bridge_id)

    def _link_call_receiver(self, bridge_id):
        bridge = self._bridge_manager.get_bridge(bridge_id)
        if len(bridge.channels) != 2:
            return

        channel_name_0 = bridge.channels[0]
        channel_name_1 = bridge.channels[1]

        channel_0 = self._innerdata.channels.get(channel_name_0)
        channel_1 = self._innerdata.channels.get(channel_name_1)

        self._call_receiver._add_channel(channel_name_0, channel_name_1,
                                         channel_0.unique_id, channel_1.unique_id)

    def _link_parse_bridge(self, bridge_id):
        bridge = self._bridge_manager.get_bridge(bridge_id)
        if len(bridge.channels) != 2:
            return

        channel_name_0 = bridge.channels[0]
        channel_name_1 = bridge.channels[1]

        self._current_call_manager.bridge_channels(
            channel_name_0,
            channel_name_1
        )

    def on_ami_bridge_leave(self, event):
        bridge_id = event['BridgeUniqueid']
        number_channels = event['BridgeNumChannels']
        channel = event['Channel']
        bridge = self._bridge_manager.get_bridge(bridge_id)

        self._unlink_call_receiver(bridge_id, number_channels)

        bridge.channels.remove(channel)

    def _unlink_call_receiver(self, bridge_id, number_channels):
        if number_channels < 2:
            bridge = self._bridge_manager.get_bridge(bridge_id)
            channel_name_0 = bridge.channels[0]
            channel_0 = self._innerdata.channels.get(channel_name_0)
            self._call_storage.end_call(channel_0.unique_id)

    def on_ami_bridge_list_item(self, event):
        bridge_id = event['BridgeUniqueid']
        self._bridge_manager._add_bridge(bridge_id)
        self._ami_class.setactionid(bridge_id)
        self._ami_class.sendcommand('BridgeInfo', [('BridgeUniqueid', bridge_id)])

    def on_ami_bridge_info_channel(self, event):
        channel = event['Channel']
        bridge_id = event['ActionID']   # ActionID is previously set to BridgeUniqueid
        bridge = self._bridge_manager.get_bridge(bridge_id)
        bridge.channels.append(channel)

    def on_ami_bridge_info_complete(self, event):
        bridge_id = event['BridgeUniqueid']
        self._update_peer_channels(bridge_id)

    def _update_channels(self, bridge_id):
        bridge = self._bridge_manager.get_bridge(bridge_id)
        if len(bridge.channels) != 2:
            return

        for channel_name in bridge.channels:
            channel = self._innerdata.channels.get(channel_name)
            if channel.properties['commstatus'] == 'linked-caller':
                self._call_form_dispatch_filter.handle_bridge(channel.unique_id, channel_name)

        for channel_name in bridge.channels:
            channel = self._innerdata.channels.get(channel_name)
            channel.properties['commstatus'] = 'linked'
            channel.properties['timestamp'] = time.time()
            self._innerdata.update(channel.channel)

        self._update_peer_channels(bridge_id)

    def _update_peer_channels(self, bridge_id):
        bridge = self._bridge_manager.get_bridge(bridge_id)
        if len(bridge.channels) != 2:
            return

        channel_name_0 = bridge.channels[0]
        channel_name_1 = bridge.channels[1]
        self._innerdata.setpeerchannel(channel_name_0, channel_name_1)
        self._innerdata.setpeerchannel(channel_name_1, channel_name_0)

    def register_ami_events(self, ami_handler):
        ami_handler.register_callback('BridgeCreate', self.on_ami_bridge_create)
        ami_handler.register_callback('BridgeDestroy', self.on_ami_bridge_destroy)
        ami_handler.register_callback('BridgeEnter', self.on_ami_bridge_enter)
        ami_handler.register_callback('BridgeLeave', self.on_ami_bridge_leave)
        ami_handler.register_callback('BridgeListItem', self.on_ami_bridge_list_item)
        ami_handler.register_callback('BridgeInfoChannel', self.on_ami_bridge_info_channel)
        ami_handler.register_callback('BridgeInfoComplete', self.on_ami_bridge_info_complete)
