# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from functools import partial
from hamcrest import assert_that, equal_to
from mock import patch, Mock, sentinel
from xivo.asterisk.extension import Extension
from xivo.asterisk.protocol_interface import InvalidChannelError
from xivo_cti.services.call.call import _Channel
from xivo_cti.services.call.receiver import CallReceiver
from xivo_cti.services.call.storage import CallStorage
from xivo_cti.model.endpoint_status import EndpointStatus


NUMBER = '3573'
CONTEXT = 'my_context'
EXTENSION = Extension(number=NUMBER, context=CONTEXT, is_internal=True)
EMPTY_EXTENSION = Extension(number='', context='', is_internal=False)
CHANNEL = 'SIP/abcd-00001'
UNIQUEID = '5765887387.56'
DEST_UNIQUEID = '123456789.56'

RINGING = EndpointStatus.ringing
AVAILABLE = EndpointStatus.available

patch_get_extension_from_channel = partial(
    patch, 'xivo_cti.services.call.helper.get_extension_from_channel',
)

patch_channel_state_status = partial(
    patch, 'xivo_cti.services.call.helper.channel_state_to_status',
)


class TestCallReceiver(unittest.TestCase):

    def setUp(self):
        self.call_storage = Mock(CallStorage)
        self.call_receiver = CallReceiver(self.call_storage)

    @patch_get_extension_from_channel(Mock(return_value=EXTENSION))
    @patch_channel_state_status(Mock(return_value=RINGING))
    def test_handle_newstate(self):
        ami_event = self._mk_new_state_event(state='5')

        self.call_receiver.handle_newstate(ami_event)

        self.call_storage.update_endpoint_status.assert_called_once_with(EXTENSION, RINGING)

    @patch_get_extension_from_channel(Mock(return_value=EXTENSION))
    @patch_channel_state_status(Mock(return_value=None))
    def test_handle_newstate_ignored(self):
        ami_event = self._mk_new_state_event()

        self.call_receiver.handle_newstate(ami_event)

        self.assertEquals(self.call_storage.update_endpoint_status.call_count, 0)

    @patch_get_extension_from_channel(
        Mock(side_effect=InvalidChannelError(sentinel.invalid_channel)))
    def test_handle_newstate_invalid_channel(self):
        ami_event = self._mk_new_state_event(sentinel.invalid_channel)

        self.call_receiver.handle_newstate(ami_event)

        self.assertEquals(self.call_storage.update_endpoint_status.call_count, 0)

    @patch_get_extension_from_channel(Mock(return_value=EMPTY_EXTENSION))
    @patch_channel_state_status(Mock(return_value=RINGING))
    def test_handle_newstate_no_extension(self):
        ami_event = self._mk_new_state_event(state='5')

        self.call_receiver.handle_newstate(ami_event)

        self.call_storage.update_endpoint_status.assert_called_once_with(EMPTY_EXTENSION, RINGING)

    @patch_get_extension_from_channel(Mock(return_value=EXTENSION))
    @patch_channel_state_status(Mock(return_value=AVAILABLE))
    def test_handle_hangup(self):
        ami_event = self._mk_hangup_event()

        self.call_receiver.handle_hangup(ami_event)

        self.call_storage.update_endpoint_status.assert_called_once_with(EXTENSION, AVAILABLE)
        self.call_storage.end_call.assert_called_once_with(UNIQUEID)

    @patch_get_extension_from_channel(
        Mock(side_effect=InvalidChannelError(sentinel.invalid_channel)))
    def test_handle_hangup_invalid_channel(self):
        ami_event = self._mk_hangup_event()

        self.call_receiver.handle_hangup(ami_event)

        self.assertEquals(self.call_storage.update_endpoint_status.call_count, 0)
        self.call_storage.end_call.assert_called_once_with(UNIQUEID)

    @patch_get_extension_from_channel()
    def test_handle_dial_begin(self, get_extension_from_channel):
        ami_event = self._mk_dial_begin_event()
        extens = {
            sentinel.channel_source: sentinel.source,
            sentinel.channel_destination: sentinel.destination,
        }
        get_extension_from_channel.side_effect = lambda channel: extens[channel]

        self.call_receiver.handle_dial_begin(ami_event)

        self.call_storage.new_call.assert_called_once_with(
            UNIQUEID,
            DEST_UNIQUEID,
            _Channel(sentinel.source, sentinel.channel_source),
            _Channel(sentinel.destination, sentinel.channel_destination),
        )

    @patch_get_extension_from_channel(Mock(side_effect=InvalidChannelError))
    def test_handle_dial_begin_invalid_channel(self):
        ami_event = self._mk_dial_begin_event()

        self.call_receiver.handle_dial_begin(ami_event)

        self.assertEquals(self.call_storage.new_call.call_count, 0)

    @patch_get_extension_from_channel()
    def test_handle_new_channel(self, get_extension_from_channel):
        get_extension_from_channel.return_value = sentinel.source_exten
        event = self._mk_new_channel_event()

        self.call_receiver.handle_new_channel(event)

        self.call_storage.new_call.assert_called_once_with(
            UNIQUEID,
            '',
            _Channel(sentinel.source_exten, sentinel.channel),
            _Channel(Extension('', '', True), '')
        )

    def test_handle_new_channel_with_a_missing_field(self):
        self.call_receiver.handle_new_channel({})

        assert_that(self.call_storage.new_call.call_count, equal_to(0))

    @patch_get_extension_from_channel()
    def test_handle_new_channel_with_an_invalid_channel(self, get_extension_from_channel):
        get_extension_from_channel.side_effect = InvalidChannelError
        event = self._mk_new_channel_event()

        self.call_receiver.handle_new_channel(event)

        assert_that(self.call_storage.new_call.call_count, equal_to(0))

    def _mk_new_channel_event(self, channel=sentinel.channel, uniqueid=UNIQUEID):
        return {
            'Event': 'NewChannel',
            'Channel': channel,
            'Uniqueid': uniqueid,
        }

    def _mk_hangup_event(self, channel=CHANNEL, uniqueid=UNIQUEID):
        return {
            'Event': 'Hangup',
            'Channel': channel,
            'Uniqueid': uniqueid,
        }

    def _mk_new_state_event(self, channel=CHANNEL, state=42):
        return {
            'Event': 'Newstate',
            'ChannelState': state,
            'Channel': channel,
        }

    def _mk_dial_begin_event(self, uniqueid=UNIQUEID,
                             dest_uniqueid=DEST_UNIQUEID,
                             source=sentinel.channel_source,
                             destination=sentinel.channel_destination):
        return {
            'Event': 'DialBegin',
            'Channel': source,
            'DestChannel': destination,
            'Uniqueid': uniqueid,
            'DestUniqueid': dest_uniqueid,
        }
