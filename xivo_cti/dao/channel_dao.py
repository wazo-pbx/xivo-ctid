# -*- coding: utf-8 -*-
# Copyright 2007-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo.asterisk.line_identity import identity_from_channel


class ChannelDAO(object):

    def __init__(self, innerdata, call_form_variable_aggregator):
        self.innerdata = innerdata
        self._call_form_variable_aggregator = call_form_variable_aggregator

    def get_caller_id_name_number(self, channel):
        if channel not in self.innerdata.channels:
            raise LookupError('Unknown channel %s' % channel)

        uid = self.innerdata.channels[channel].unique_id
        return self._get(uid, 'calleridname'), self._get(uid, 'calleridnum')

    def get_channel_from_unique_id(self, unique_id):
        for channel_id, channel in self.innerdata.channels.iteritems():
            if channel.unique_id != unique_id:
                continue
            return channel_id
        raise LookupError('No channel with unique id %s' % unique_id)

    def channels_from_identity(self, identity):
        identity = identity.lower()
        return [channel for channel in self.innerdata.channels
                if identity_from_channel(channel) == identity]

    def _get(self, uid, var):
        channel_data = self._call_form_variable_aggregator.get(uid)
        return channel_data['xivo'].get(var, '')
