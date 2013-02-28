# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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
from xivo_cti.cti_anylist import ContextAwareAnyList

logger = logging.getLogger('agentlist')


class AgentsList(ContextAwareAnyList):

    def __init__(self, innerdata):
        self._innerdata = innerdata
        ContextAwareAnyList.__init__(self, 'agents')

    def init_data(self):
        super(AgentsList, self).init_data()
        self._init_reverse_dictionary()

    def add(self, agent_id):
        super(AgentsList, self).add(agent_id)
        self._add_to_reverse_dictionary(agent_id)

    def delete(self, agent_id):
        self._remove_from_reverse_dictionary(agent_id)
        super(AgentsList, self).delete(agent_id)

    def _init_reverse_dictionary(self):
        self.reverse_index = {}
        for agent_id, agent in self.keeplist.iteritems():
            agent_number = agent['number']
            self.reverse_index[agent_number] = agent_id

    def _add_to_reverse_dictionary(self, agent_id):
        agent = self.keeplist[agent_id]
        agent_number = agent['number']
        self.reverse_index[agent_number] = agent_id

    def _remove_from_reverse_dictionary(self, agent_id):
        agent = self.keeplist[agent_id]
        agent_number = agent['number']
        del self.reverse_index[agent_number]

    def idbyagentnumber(self, agentnumber):
        idx = self.reverse_index.get(agentnumber)
        if idx in self.keeplist:
            return idx

    def get_agent_by_user(self, user_id):
        user = self._innerdata.xod_config['users'].keeplist[str(user_id)]
        return self.keeplist.get(user['agentid'])
