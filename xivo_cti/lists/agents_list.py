# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti_anylist import ContextAwareAnyList


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
