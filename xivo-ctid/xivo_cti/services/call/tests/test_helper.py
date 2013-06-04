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

from xivo_cti.services.call import helper
from xivo_cti.services.call.helper import ChannelState
from xivo_cti.model.endpoint_status import EndpointStatus


class TestCallHelper(unittest.TestCase):

    def test_interface_from_channel_sip(self):
        channel = 'SIP/askdjhf-3216549'
        expected_interface = 'SIP/askdjhf'

        result = helper.interface_from_channel(channel)

        self.assertEquals(expected_interface, result)

    def test_interface_from_channel_sccp(self):
        channel = 'sccp/13486@SEP6556DEADBEEF-658'
        expected_interface = 'sccp/13486@SEP6556DEADBEEF'

        result = helper.interface_from_channel(channel)

        self.assertEquals(expected_interface, result)

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

    def test_channel_state_to_status_unknown(self):
        channel_state = 'unknown'
        expected_status = None

        result = helper.channel_state_to_status(channel_state)

        self.assertEquals(expected_status, result)
