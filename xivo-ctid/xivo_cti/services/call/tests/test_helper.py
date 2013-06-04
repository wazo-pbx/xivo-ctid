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

from mock import patch
from xivo.asterisk.extension import Extension
from xivo_cti.services.call import helper
from xivo_cti.services.call.helper import ChannelState
from xivo_cti.services.call.helper import InvalidChannel
from xivo_cti.services.call.helper import ProtocolInterface
from xivo_cti.model.endpoint_status import EndpointStatus


class TestCallHelper(unittest.TestCase):

    def test_protocol_interface_from_channel_sip(self):
        channel = 'SIP/askdjhf-3216549'
        expected_result = ProtocolInterface('SIP', 'askdjhf')

        result = helper.protocol_interface_from_channel(channel)

        self.assertEquals(expected_result, result)

    def test_protocol_interface_from_channel_sccp(self):
        channel = 'sccp/13486@SEP6556DEADBEEF-658'
        expected_result = ProtocolInterface('sccp', '13486')

        result = helper.protocol_interface_from_channel(channel)

        self.assertEquals(expected_result, result)

    def test_protocol_interface_from_channel_invalid(self):
        invalid_channel = 'slkdfjaslkdjfaslkdjflskdjf'

        self.assertRaises(InvalidChannel, helper.protocol_interface_from_channel, invalid_channel)

    def test_channel_state_to_status_ring(self):
        channel_state = ChannelState.ring
        expected_status = EndpointStatus.ringback_tone

        result = helper.channel_state_to_status(channel_state)

        self.assertEquals(expected_status, result)

    def test_channel_state_to_status_ringing(self):
        channel_state = ChannelState.ringing
        expected_status = EndpointStatus.ringing

        result = helper.channel_state_to_status(channel_state)

        self.assertEquals(expected_status, result)

    def test_channel_state_to_status_talking(self):
        channel_state = ChannelState.talking
        expected_status = EndpointStatus.talking

        result = helper.channel_state_to_status(channel_state)

        self.assertEquals(expected_status, result)

    def test_channel_state_to_status_unknown(self):
        channel_state = 'unknown'
        expected_status = None

        result = helper.channel_state_to_status(channel_state)

        self.assertEquals(expected_status, result)

    @patch('xivo_dao.line_dao.get_extension_from_protocol_interface')
    def test_get_extension_from_channel_invalid(self, dao_get_extension):
        channel = 'asopwasfhasl;jfhofh'
        expected_extension = Extension('1000', 'my_context')
        dao_get_extension.return_value = expected_extension

        self.assertRaises(InvalidChannel, helper.get_extension_from_channel, channel)

    @patch('xivo_dao.line_dao.get_extension_from_protocol_interface')
    def test_get_extension_from_channel_no_extension(self, dao_get_extension):
        channel = 'SIP/asdlkfj-532486'
        dao_get_extension.side_effect = LookupError

        self.assertRaises(LookupError, helper.get_extension_from_channel, channel)

    @patch('xivo_dao.line_dao.get_extension_from_protocol_interface')
    def test_get_extension_from_channel(self, dao_get_extension):
        channel = 'SIP/asdlkfj-532486'
        expected_extension = Extension('1000', 'my_context')
        dao_get_extension.return_value = expected_extension

        result = helper.get_extension_from_channel(channel)

        dao_get_extension.assert_called_once_with('SIP', 'asdlkfj')
        self.assertEquals(expected_extension, result)
