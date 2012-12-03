# -*- coding: utf-8 -*-

import unittest
import time
from mock import patch

from xivo_cti.services.current_call import manager


class TestCurrentCallManager(unittest.TestCase):

    @patch('time.time')
    def test_bridge_channels(self, mock_time):
        channel_1 = 'SIP/tc8nb4-00000004'
        channel_2 = 'SIP/6s7foq-00000005'
        bridge_time = time.time()
        mock_time.return_value = bridge_time
        current_call_manager = manager.CurrentCallManager()

        current_call_manager.bridge_channels(channel_1, channel_2)

        expected = {
            channel_1: [
                {'channel': channel_2,
                 'bridge_time': bridge_time,
                 'on_hold': False}
            ],
            channel_2: [
                {'channel': channel_1,
                 'bridge_time': bridge_time,
                 'on_hold': False}
            ],
        }

        self.assertEqual(current_call_manager._channels, expected)

    def test_hold_channel(self):
        channel_1 = 'SIP/tc8nb4-00000004'
        channel_2 = 'SIP/6s7foq-00000005'
        current_call_manager = manager.CurrentCallManager()
        current_call_manager._channels = {
            channel_1: [
                {'channel': channel_2,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
            channel_2: [
                {'channel': channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        current_call_manager.hold_channel(channel_2)

        expected = {
            channel_1: [
                {'channel': channel_2,
                 'bridge_time': 1234,
                 'on_hold': True}
            ],
            channel_2: [
                {'channel': channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        self.assertEqual(current_call_manager._channels, expected)

    def test_unhold_channel(self):
        channel_1 = 'SIP/tc8nb4-00000004'
        channel_2 = 'SIP/6s7foq-00000005'
        current_call_manager = manager.CurrentCallManager()
        current_call_manager._channels = {
            channel_1: [
                {'channel': channel_2,
                 'bridge_time': 1234,
                 'on_hold': True}
            ],
            channel_2: [
                {'channel': channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        current_call_manager.unhold_channel(channel_2)

        expected = {
            channel_1: [
                {'channel': channel_2,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
            channel_2: [
                {'channel': channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        self.assertEqual(current_call_manager._channels, expected)

    def test_unbridge_channels(self):
        channel_1 = 'SIP/tc8nb4-00000004'
        channel_2 = 'SIP/6s7foq-00000005'
        current_call_manager = manager.CurrentCallManager()
        current_call_manager._channels = {
            channel_1: [
                {'channel': channel_2,
                 'bridge_time': 1234,
                 'on_hold': True}
            ],
            channel_2: [
                {'channel': channel_1,
                 'bridge_time': 1234,
                 'on_hold': False}
            ],
        }

        current_call_manager.unbridge_channels(channel_1, channel_2)

        expected = {
        }

        self.assertEqual(current_call_manager._channels, expected)
