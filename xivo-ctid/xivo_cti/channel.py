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

import time


class Channel(object):

    extra_vars = {'xivo': ['agentnumber', 'calledidname', 'calledidnum',
                           'calleridname', 'calleridnum', 'calleridrdnis',
                           'calleridton', 'channel', 'context', 'date',
                           'destid', 'desttype', 'did', 'direction',
                           'directory', 'ipbxid', 'origin', 'queuename', 'time',
                           'uniqueid', 'userid', 'where'],
                  'dp': [],
                  'db': []}

    def __init__(self, channel, context, unique_id=None):
        self.channel = channel
        self.peerchannel = None
        self.context = context
        self.unique_id = unique_id
        # destlist to update along the incoming channel path, in order
        # to be ready when a sheet will be sent to the 'destination'

        self.properties = {
            'holded': False,
            'parked': False,
            'direction': None,
            'commstatus': 'ready',
            'timestamp': time.time(),
            'talkingto_kind': None,
            'talkingto_id': None,
            'state': 'Unknown',
        }
        self.relations = []
        self.extra_data = {}

    def setparking(self, exten, parkinglot):
        self.properties['parked'] = True
        self.properties['talkingto_kind'] = 'parking'
        self.properties['talkingto_id'] = '%s@%s' % (exten, parkinglot)

    def unsetparking(self):
        self.properties['parked'] = False
        self.properties['talkingto_kind'] = None
        self.properties['talkingto_id'] = None

    def addrelation(self, relation):
        if relation not in self.relations:
            self.relations.append(relation)

    def delrelation(self, relation):
        if relation in self.relations:
            self.relations.remove(relation)

    def update_state(self, state, description):
        # values
        # 0 Down (creation time)
        # 5 Ringing
        # 6 Up
        self.state = state
        if description:
            self.properties['state'] = description

    # extra dialplan data that may be reachable from sheets

    def set_extra_data(self, family, varname, varvalue):
        if family not in self.extra_vars:
            return
        if family not in self.extra_data:
            self.extra_data[family] = {}
        if family == 'xivo':
            if varname in self.extra_vars.get(family):
                self.extra_data[family][varname] = varvalue
        else:
            self.extra_data[family][varname] = varvalue

    def has_extra_data(self, family, varname):
        return family in self.extra_data and varname in self.extra_data[family]

    def inherit(self, parent_channel):
        for (parent_key, parent_value) in parent_channel.extra_data.iteritems():
            for parent_subkey, parent_subvalue in parent_value.iteritems():
                self.set_extra_data(parent_key, parent_subkey, parent_subvalue)
