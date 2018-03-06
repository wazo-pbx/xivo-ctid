# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock
from xivo_cti.services.bridge.manager import BridgeManager
from xivo_cti.services.bridge.updater import BridgeUpdater
from xivo_cti.xivo_ami import AMIClass


class TestBridgeUpdater(unittest.TestCase):

    def setUp(self):
        self.bridge_id = 'e136cd36-5187-430c-af2a-d1f08870847b'
        self.bridge_type = 'basic'
        self.channel_name = 'SIP/abc-123'
        self.ami_class = Mock(AMIClass)
        self.bridge_manager = Mock(BridgeManager)
        self.bridge_updater = BridgeUpdater(self.ami_class,
                                            self.bridge_manager)

    def test_on_ami_bridge_create(self):
        ami_event = {
            'BridgeUniqueid': self.bridge_id,
            'BridgeType': self.bridge_type,
        }

        self.bridge_updater.on_ami_bridge_create(ami_event)

        self.bridge_manager._on_bridge_create.assert_called_once_with(self.bridge_id, self.bridge_type)

    def test_on_ami_bridge_destroy(self):
        ami_event = {
            'BridgeUniqueid': self.bridge_id,
        }

        self.bridge_updater.on_ami_bridge_destroy(ami_event)

        self.bridge_manager._on_bridge_destroy.assert_called_once_with(self.bridge_id)

    def test_on_ami_bridge_enter(self):
        ami_event = {
            'BridgeUniqueid': self.bridge_id,
            'Channel': self.channel_name
        }

        self.bridge_updater.on_ami_bridge_enter(ami_event)

        self.bridge_manager._on_bridge_enter.assert_called_once_with(self.bridge_id, self.channel_name)

    def test_on_ami_bridge_leave(self):
        ami_event = {
            'BridgeUniqueid': self.bridge_id,
            'Channel': self.channel_name
        }

        self.bridge_updater.on_ami_bridge_leave(ami_event)

        self.bridge_manager._on_bridge_leave.assert_called_once_with(self.bridge_id, self.channel_name)

    def test_on_ami_bridge_list_item(self):
        ami_event = {
            'BridgeUniqueid': self.bridge_id,
            'BridgeType': self.bridge_type,
        }

        self.bridge_updater.on_ami_bridge_list_item(ami_event)

        self.bridge_manager._add_bridge.assert_called_once_with(self.bridge_id, self.bridge_type)
        self.ami_class.sendcommand.assert_called_once_with('BridgeInfo', [('BridgeUniqueid', self.bridge_id)])

    def test_on_ami_bridge_info_channel(self):
        ami_event = {
            'ActionID': 'e136cd36-5187-430c-af2a-d1f08870847b',
            'Channel': self.channel_name,
        }

        self.bridge_updater.on_ami_bridge_info_channel(ami_event)

        self.bridge_manager._add_channel_to_bridge.assert_called_once_with(self.bridge_id, self.channel_name)
