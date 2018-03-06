# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, patch, sentinel
from xivo.asterisk.extension import Extension
from xivo_cti.services.call import helper
from xivo_cti.services.call.helper import ChannelState
from xivo_cti.model.endpoint_status import EndpointStatus
from xivo.asterisk.protocol_interface import InvalidChannelError


class TestCallHelper(unittest.TestCase):

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
    def test_get_extension_from_channel_invalid(self, _dao_get_extension):
        channel = 'asopwasfhasl;jfhofh'

        self.assertRaises(InvalidChannelError, helper.get_extension_from_channel, channel)

    @patch('xivo_dao.line_dao.get_extension_from_protocol_interface')
    def test_get_extension_from_channel_no_extension(self, dao_get_extension):
        channel = 'SIP/asdlkfj-532486'
        dao_get_extension.side_effect = LookupError
        expected_result = Extension(number='', context='', is_internal=False)

        result = helper.get_extension_from_channel(channel)

        self.assertEquals(expected_result, result)

    @patch('xivo_dao.line_dao.get_extension_from_protocol_interface')
    def test_get_extension_from_channel(self, dao_get_extension):
        channel = 'SIP/asdlkfj-532486'
        expected_extension = Mock()
        dao_get_extension.return_value = expected_extension

        result = helper.get_extension_from_channel(channel)

        dao_get_extension.assert_called_once_with('SIP', 'asdlkfj')
        self.assertEquals(expected_extension, result)

    @patch('xivo_dao.line_dao.get_extension_from_protocol_interface',
           Mock(side_effect=ValueError('Invalid proto')))
    def test_get_extension_from_local_channel(self):
        channel = 'Local/id-5@agentcallback-38974358734;2'
        expected_extension = Extension('', '', False)

        result = helper.get_extension_from_channel(channel)

        self.assertEquals(expected_extension, result)
