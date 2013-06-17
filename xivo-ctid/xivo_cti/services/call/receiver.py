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

import logging

from xivo_cti.services.call import helper
from xivo_cti.services.call.helper import InvalidChannel
from xivo_cti.model.endpoint_status import EndpointStatus

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

        self._update_channel_status(channel, status)

    def _update_channel_status(self, channel, status):
        try:
            extension = helper.get_extension_from_channel(channel)
        except (InvalidChannel) as e:
            logger.error(e)
        else:
            self._call_storage.update_endpoint_status(extension, status)

    def handle_dial(self, event):
        if event['SubEvent'] == 'Begin':
            self._handle_dial_begin(event)
        elif event['SubEvent'] == 'End':
            self._handle_dial_end(event)

    def _handle_dial_begin(self, event):
        channel_source = event['Channel']
        channel_destination = event['Destination']
        uniqueid = event['UniqueID']

        try:
            extension_source = helper.get_extension_from_channel(channel_source)
            extension_destination = helper.get_extension_from_channel(channel_destination)
        except (InvalidChannel) as e:
            logger.error(e)
        else:
            self._call_storage.new_call(uniqueid=uniqueid,
                                        source=extension_source,
                                        destination=extension_destination)

    def _handle_dial_end(self, event):
        uniqueid = event['UniqueID']
        self._call_storage.end_call(uniqueid)
