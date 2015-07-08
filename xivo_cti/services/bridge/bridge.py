# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

from xivo_cti.channel import ChannelRole

logger = logging.getLogger(__name__)


class Bridge(object):

    def __init__(self, bridge_id, bridge_type):
        self.bridge_id = bridge_id
        self.bridge_type = bridge_type
        self.channels = []

    # package private method
    def _add_channel(self, channel):
        self.channels.append(channel)

    # package private method
    def _remove_channel(self, channel):
        try:
            self.channels.remove(channel)
        except ValueError:
            logger.error('failed to remove channel %s from bridge %s: no such channel',
                         channel.channel, self.bridge_id)

    def linked(self):
        return self.bridge_type == 'basic' and len(self.channels) == 2

    def get_caller_channel(self):
        channel_1, channel_2 = self.channels
        if channel_1.role == ChannelRole.callee or channel_2.role == ChannelRole.caller:
            return channel_2
        else:
            return channel_1

    def get_callee_channel(self):
        channel_1, channel_2 = self.channels
        if channel_1.role == ChannelRole.callee or channel_2.role == ChannelRole.caller:
            return channel_1
        else:
            return channel_2
