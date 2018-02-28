# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+


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

    def register_ami_events(self, ami_handler):
        ami_handler.register_callback('BridgeCreate', self.on_ami_bridge_create)
        ami_handler.register_callback('BridgeDestroy', self.on_ami_bridge_destroy)
        ami_handler.register_callback('BridgeEnter', self.on_ami_bridge_enter)
        ami_handler.register_callback('BridgeLeave', self.on_ami_bridge_leave)
        ami_handler.register_callback('BridgeListItem', self.on_ami_bridge_list_item)
        ami_handler.register_callback('BridgeInfoChannel', self.on_ami_bridge_info_channel)
