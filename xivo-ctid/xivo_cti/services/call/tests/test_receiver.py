# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

import unittest

from mock import patch, Mock
from xivo_cti.services.call.receiver import CallReceiver
from xivo_cti.services.call.helper import InvalidChannel
from xivo_cti.services.call.notifier import CallNotifier
from xivo_cti.services.call.storage import CallStorage
from xivo_cti.model.endpoint_status import EndpointStatus
from xivo.asterisk.extension import Extension


class TestCallReceiver(unittest.TestCase):

    def setUp(self):
        self.call_storage = Mock(CallStorage)
        self.call_notifier = Mock(CallNotifier)
        self.call_receiver = CallReceiver(self.call_storage, self.call_notifier)

    @patch('xivo_cti.services.call.helper.get_extension_from_channel')
    @patch('xivo_cti.services.call.helper.channel_state_to_status')
    def test_handle_newstate(self, channel_state_to_status, get_extension_from_channel):
        extension = Extension('1000', 'default')
        channel = "SIP/abcd-00001"
        call_status = EndpointStatus.ringing

        get_extension_from_channel.return_value = extension
        channel_state_to_status.return_value = call_status

        ami_event = {
            'Event': 'Newstate',
            'ChannelState': '5',
            'Channel': channel,
        }

        self.call_receiver.handle_newstate(ami_event)

        self.call_storage.update_endpoint_status.assert_called_once_with(extension, call_status)

    @patch('xivo_cti.services.call.helper.get_extension_from_channel')
    @patch('xivo_cti.services.call.helper.channel_state_to_status')
    def test_handle_newstate_ignored(self, channel_state_to_status, get_extension_from_channel):
        extension = Extension('1000', 'default')
        channel = "SIP/abcd-00001"

        get_extension_from_channel.return_value = extension
        channel_state_to_status.return_value = None

        ami_event = {
            'Event': 'Newstate',
            'ChannelState': '42',
            'Channel': channel,
        }

        self.call_receiver.handle_newstate(ami_event)

        self.assertEquals(self.call_storage.update_endpoint_status.call_count, 0)

    @patch('xivo_cti.services.call.helper.get_extension_from_channel')
    @patch('xivo_cti.services.call.helper.channel_state_to_status')
    def test_handle_newstate_invalid_channel(self, channel_state_to_status, get_extension_from_channel):
        channel = 'aslkdjfas;ldfh'
        get_extension_from_channel.side_effect = InvalidChannel(channel)
        ami_event = {
            'Event': 'Newstate',
            'ChannelState': '42',
            'Channel': channel
        }

        self.call_receiver.handle_newstate(ami_event)

        self.assertEquals(self.call_storage.update_endpoint_status.call_count, 0)

    @patch('xivo_cti.services.call.helper.get_extension_from_channel')
    @patch('xivo_cti.services.call.helper.channel_state_to_status')
    def test_handle_newstate_no_extension(self, channel_state_to_status, get_extension_from_channel):
        get_extension_from_channel.side_effect = LookupError()
        ami_event = {
            'Event': 'Newstate',
            'ChannelState': '5',
            'Channel': 'SIP/abcd-00001'
        }

        self.call_receiver.handle_newstate(ami_event)

        self.assertEquals(self.call_storage.update_endpoint_status.call_count, 0)

    @patch('xivo_cti.services.call.helper.get_extension_from_channel')
    @patch('xivo_cti.services.call.helper.channel_state_to_status')
    def test_handle_hangup(self, channel_state_to_status, get_extension_from_channel):
        extension = Extension('1000', 'default')
        channel = "SIP/abcd-00001"
        call_status = EndpointStatus.available

        get_extension_from_channel.return_value = extension
        channel_state_to_status.return_value = call_status

        ami_event = {
            'Event': 'Hangup',
            'Channel': channel,
        }

        self.call_receiver.handle_hangup(ami_event)

        self.call_storage.update_endpoint_status.assert_called_once_with(extension, call_status)

    @patch('xivo_cti.services.call.helper.get_extension_from_channel')
    @patch('xivo_cti.services.call.helper.channel_state_to_status')
    def test_handle_hangup_invalid_channel(self, channel_state_to_status, get_extension_from_channel):
        channel = 'aslkdjfas;ldfh'
        get_extension_from_channel.side_effect = InvalidChannel(channel)
        ami_event = {
            'Event': 'Hangup',
            'Channel': channel,
        }

        self.call_receiver.handle_hangup(ami_event)

        self.assertEquals(self.call_storage.update_endpoint_status.call_count, 0)

    @patch('xivo_cti.services.call.helper.get_extension_from_channel')
    @patch('xivo_cti.services.call.helper.channel_state_to_status')
    def test_handle_hangup_no_extension(self, channel_state_to_status, get_extension_from_channel):
        get_extension_from_channel.side_effect = LookupError()
        ami_event = {
            'Event': 'Hangup',
            'Channel': 'SIP/abcd-00001'
        }

        self.call_receiver.handle_hangup(ami_event)

        self.assertEquals(self.call_storage.update_endpoint_status.call_count, 0)
