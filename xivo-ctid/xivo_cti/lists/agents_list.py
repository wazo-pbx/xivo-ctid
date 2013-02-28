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
        ContextAwareAnyList.init_data(self)
        self.reverse_index = {}
        for idx, ag in self.keeplist.iteritems():
            if ag['number'] not in self.reverse_index:
                self.reverse_index[ag['number']] = idx
            else:
                logger.warning('2 agents have the same number')

    def idbyagentnumber(self, agentnumber):
        idx = self.reverse_index.get(agentnumber)
        if idx in self.keeplist:
            return idx

    def get_agent_by_user(self, user_id):
        user = self._innerdata.xod_config['users'].keeplist[str(user_id)]
        return self.keeplist.get(user['agentid'])
