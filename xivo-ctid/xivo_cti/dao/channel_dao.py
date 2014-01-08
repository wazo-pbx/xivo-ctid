# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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


class ChannelDAO(object):

    def __init__(self, innerdata, call_form_variable_aggregator):
        self.innerdata = innerdata
        self._call_form_variable_aggregator = call_form_variable_aggregator

    def get_caller_id_name_number(self, channel):
        if channel not in self.innerdata.channels:
            raise LookupError('Unknown channe %s' % channel)

        uid = self.innerdata.channels[channel].unique_id
        return self._get(uid, 'calleridname'), self._get(uid, 'calleridnum')

    def get_channel_from_unique_id(self, unique_id):
        for channel_id, channel in self.innerdata.channels.iteritems():
            if channel.unique_id != unique_id:
                continue
            return channel_id
        raise LookupError('No channel with unique id %s' % unique_id)

    def _get(self, uid, var):
        channel_data = self._call_form_variable_aggregator.get(uid)
        return channel_data['xivo'].get(var, '')
