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

logger = logging.getLogger(__name__)


class Bridge(object):

    def __init__(self, bridge_id, bridge_type):
        self.bridge_id = bridge_id
        self.bridge_type = bridge_type
        self.channels = []

    def add_channel(self, channel_name):
        self.channels.append(channel_name)

    def remove_channel(self, channel_name):
        try:
            self.channels.remove(channel_name)
        except ValueError:
            logger.warning('Failed to remove channel %s from bridge %s: no such channel',
                           channel_name, self.bridge_id)

    def basic_channels_connected(self):
        return self.bridge_type == 'basic' and len(self.channels) == 2
