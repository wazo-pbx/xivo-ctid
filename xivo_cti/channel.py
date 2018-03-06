# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+


class ChannelRole(object):

    unknown = 'unknown'
    caller = 'caller'
    callee = 'callee'


class Channel(object):

    def __init__(self, channel, context, unique_id):
        self.channel = channel
        self.context = context
        self.unique_id = unique_id
        self.role = ChannelRole.unknown
