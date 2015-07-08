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


class BridgeUpdater(object):

    def __init__(self, ami_class, bridge_manager):
        self._ami_class = ami_class
        self._bridge_manager = bridge_manager

    def on_ami_bridge_create(self, event):
        bridge_id = event['BridgeUniqueid']
        bridge_type = event['BridgeType']
        self._bridge_manager._on_bridge_create(bridge_id, bridge_type)

    def on_ami_bridge_destroy(self, event):
        bridge_id = event['BridgeUniqueid']
        self._bridge_manager._on_bridge_destroy(bridge_id)

    def on_ami_bridge_enter(self, event):
        bridge_id = event['BridgeUniqueid']
        channel_name = event['Channel']
        self._bridge_manager._on_bridge_enter(bridge_id, channel_name)

    def on_ami_bridge_leave(self, event):
        bridge_id = event['BridgeUniqueid']
        channel_name = event['Channel']
        self._bridge_manager._on_bridge_leave(bridge_id, channel_name)

    def on_ami_bridge_list_item(self, event):
        bridge_id = event['BridgeUniqueid']
        bridge_type = event['BridgeType']
        self._bridge_manager._add_bridge(bridge_id, bridge_type)
        self._ami_class.setactionid(bridge_id)
        self._ami_class.sendcommand('BridgeInfo', [('BridgeUniqueid', bridge_id)])

    def on_ami_bridge_info_channel(self, event):
        channel = event['Channel']
        bridge_id = event['ActionID']   # ActionID is previously set to BridgeUniqueid
        self._bridge_manager._add_channel_to_bridge(bridge_id, channel)

    def on_ami_bridge_info_complete(self, event):
        bridge_id = event['BridgeUniqueid']
        self._bridge_manager._finish_bridge_initialization(bridge_id)

    def register_ami_events(self, ami_handler):
        ami_handler.register_callback('BridgeCreate', self.on_ami_bridge_create)
        ami_handler.register_callback('BridgeDestroy', self.on_ami_bridge_destroy)
        ami_handler.register_callback('BridgeEnter', self.on_ami_bridge_enter)
        ami_handler.register_callback('BridgeLeave', self.on_ami_bridge_leave)
        ami_handler.register_callback('BridgeListItem', self.on_ami_bridge_list_item)
        ami_handler.register_callback('BridgeInfoChannel', self.on_ami_bridge_info_channel)
        ami_handler.register_callback('BridgeInfoComplete', self.on_ami_bridge_info_complete)
