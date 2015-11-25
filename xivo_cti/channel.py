# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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


class ChannelRole(object):

    unknown = 'unknown'
    caller = 'caller'
    callee = 'callee'


class Channel(object):

    def __init__(self, channel, context, unique_id=None):
        self.channel = channel
        self.peerchannel = None
        self.context = context
        self.unique_id = unique_id
        self.role = ChannelRole.unknown
        # destlist to update along the incoming channel path, in order
        # to be ready when a sheet will be sent to the 'destination'
        self.relations = []

    def addrelation(self, relation):
        if relation not in self.relations:
            self.relations.append(relation)

    def delrelation(self, relation):
        if relation in self.relations:
            self.relations.remove(relation)

    def update_state(self, state):
        # values
        # 0 Down (creation time)
        # 5 Ringing
        # 6 Up
        self.state = state
