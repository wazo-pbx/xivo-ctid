# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
