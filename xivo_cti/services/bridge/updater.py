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

    def __init__(self, ami_class, bridge_manager, call_form_dispatch_filter,
                 call_receiver, call_storage, current_call_manager, innerdata):
        self._ami_class = ami_class
        self._bridge_manager = bridge_manager
        self._call_form_dispatch_filter = call_form_dispatch_filter
        self._call_receiver = call_receiver
        self._call_storage = call_storage
        self._current_call_manager = current_call_manager
        self._innerdata = innerdata

    def on_ami_bridge_create(self, event):
        bridge_id = event['BridgeUniqueid']
        bridge_type = event['BridgeType']
        self._bridge_manager._add_bridge(bridge_id, bridge_type)

    def on_ami_bridge_destroy(self, event):
        bridge_id = event['BridgeUniqueid']
        self._bridge_manager._remove_bridge(bridge_id)

    def on_ami_bridge_enter(self, event):
        bridge_id = event['BridgeUniqueid']
        channel_name = event['Channel']
        bridge = self._bridge_manager.get_bridge(bridge_id)
        bridge.add_channel(channel_name)

        if bridge.basic_channels_connected():
            self._update_channels(bridge)
            self._link_call_receiver(bridge)

    def _update_channels(self, bridge):
        for channel_name in bridge.channels:
            channel = self._innerdata.channels.get(channel_name)
            if channel.properties['commstatus'] == 'calling':
                self._call_form_dispatch_filter.handle_bridge(channel.unique_id, channel_name)

            channel.properties['commstatus'] = 'linked'
            channel.properties['timestamp'] = time.time()
            self._innerdata.update(channel.channel)

        self._update_peer_channels(bridge)

    def _link_call_receiver(self, bridge):
        channel_name_0 = bridge.channels[0]
        channel_name_1 = bridge.channels[1]

        channel_0 = self._innerdata.channels.get(channel_name_0)
        channel_1 = self._innerdata.channels.get(channel_name_1)

        self._call_receiver._add_channel(channel_name_0, channel_name_1,
                                         channel_0.unique_id, channel_1.unique_id)

        self._current_call_manager.bridge_channels(channel_name_0,
                                                   channel_name_1)

    def on_ami_bridge_leave(self, event):
        bridge_id = event['BridgeUniqueid']
        number_channels = event['BridgeNumChannels']
        channel_name = event['Channel']
        unique_id = event['Uniqueid']

        bridge = self._bridge_manager.get_bridge(bridge_id)
        bridge.remove_channel(channel_name)

        if number_channels < 2:
            self._call_storage.end_call(unique_id)

    def on_ami_bridge_list_item(self, event):
        bridge_id = event['BridgeUniqueid']
        bridge_type = event['BridgeType']
        self._bridge_manager._add_bridge(bridge_id, bridge_type)
        self._ami_class.setactionid(bridge_id)
        self._ami_class.sendcommand('BridgeInfo', [('BridgeUniqueid', bridge_id)])

    def on_ami_bridge_info_channel(self, event):
        channel = event['Channel']
        bridge_id = event['ActionID']   # ActionID is previously set to BridgeUniqueid
        bridge = self._bridge_manager.get_bridge(bridge_id)
        bridge.add_channel(channel)

    def on_ami_bridge_info_complete(self, event):
        bridge_id = event['BridgeUniqueid']
        bridge = self._bridge_manager.get_bridge(bridge_id)
        if bridge.basic_channels_connected():
            self._update_peer_channels(bridge)

    def _update_peer_channels(self, bridge):
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
