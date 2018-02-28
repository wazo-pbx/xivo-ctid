# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_cti.services.call import helper
from xivo_cti.services.call.call import _Channel
from xivo.asterisk.extension import Extension
from xivo_cti.model.endpoint_status import EndpointStatus
from xivo.asterisk.protocol_interface import InvalidChannelError

logger = logging.getLogger(__name__)


class CallReceiver(object):

    def __init__(self, call_storage):
        self._call_storage = call_storage

    def handle_newstate(self, event):
        channel = event['Channel']
        status = helper.channel_state_to_status(event['ChannelState'])

        if status is not None:
            self._update_channel_status(channel, status)

    def handle_hangup(self, event):
        channel = event['Channel']
        status = EndpointStatus.available
        uniqueid = event['Uniqueid']

        self._update_channel_status(channel, status)
        self._call_storage.end_call(uniqueid)

    def _update_channel_status(self, channel, status):
        try:
            extension = helper.get_extension_from_channel(channel)
        except (InvalidChannelError) as e:
            logger.error(e)
        else:
            self._call_storage.update_endpoint_status(extension, status)

    def handle_dial_begin(self, event):
        channel_source = event.get('Channel')
        if channel_source is None:
            # If there are no channel, it's a dial initiated by an Originate
            return
        channel_destination = event['DestChannel']
        destination_uniqueid = event['DestUniqueid']
        uniqueid = event['Uniqueid']

        self._add_channel(channel_source, channel_destination, uniqueid, destination_uniqueid)

    def handle_new_channel(self, event):
        try:
            channel = event['Channel']
            unique_id = event['Uniqueid']
            source_exten = helper.get_extension_from_channel(channel)
        except (InvalidChannelError, KeyError):
            logger.debug('ignoring %s', event)
            return

        self._call_storage.new_call(
            unique_id,
            '',
            _Channel(source_exten, channel),
            _Channel(Extension('', '', True), ''),
        )

    def _add_channel(self, channel_source, channel_destination, uniqueid, destination_uniqueid):
        try:
            extension_source = helper.get_extension_from_channel(channel_source)
            extension_destination = helper.get_extension_from_channel(channel_destination)
        except (InvalidChannelError) as e:
            logger.error(e)
        else:
            self._call_storage.new_call(
                uniqueid,
                destination_uniqueid,
                _Channel(extension_source, channel_source),
                _Channel(extension_destination, channel_destination),
            )

    def handle_bridge_link(self, bridge_event):
        channel_source = bridge_event.bridge.get_caller_channel()
        channel_destination = bridge_event.bridge.get_callee_channel()
        self._add_channel(channel_source.channel, channel_destination.channel,
                          channel_source.unique_id, channel_destination.unique_id)

    def handle_bridge_unlink(self, bridge_event):
        self._call_storage.end_call(bridge_event.channel.unique_id)
        for channel in bridge_event.bridge.channels:
            self._call_storage.end_call(channel.unique_id)
