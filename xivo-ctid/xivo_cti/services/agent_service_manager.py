# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from xivo_cti.tools.idconverter import IdConverter
from xivo_dao import userfeatures_dao

logger = logging.getLogger('Agent Manager')


class AgentServiceManager(object):

    def __init__(self,
                 agent_executor,
                 agent_features_dao,
                 innerdata_dao,
                 line_features_dao):
        self.agent_executor = agent_executor
        self.agent_features_dao = agent_features_dao
        self.innerdata_dao = innerdata_dao
        self.line_features_dao = line_features_dao

    def on_cti_agent_login(self, user_id, agent_xid=None, agent_exten=None):
        agent_id = self._transform_agent_xid(user_id, agent_xid)
        if not agent_id:
            logger.info('%s not an agent (%s)', agent_xid, agent_exten)
            return 'error', {'error_string': 'invalid_exten',
                             'class': 'ipbxcommand'}
        if not agent_exten:
            extens = self.find_agent_exten(agent_id)
            agent_exten = extens[0] if extens else None

        if not self.line_features_dao.is_phone_exten(agent_exten):
            logger.info('%s tried to login with wrong exten (%s)', agent_id, agent_exten)
            return 'error', {'error_string': 'invalid_exten',
                             'class': 'ipbxcommand'}

        self.login(agent_id, agent_exten, self.agent_features_dao.agent_context(agent_id))

    def on_cti_agent_logout(self, user_id, agent_xid=None):
        agent_id = self._transform_agent_xid(user_id, agent_xid)
        if not agent_id:
            logger.info('%s not an agent', agent_xid)
            return 'error', {'error_string': 'invalid_exten',
                             'class': 'ipbxcommand'}

        self.logoff(agent_id)

    def _transform_agent_xid(self, user_id, agent_id):
        if not agent_id or agent_id == 'agent:special:me':
            agent_id = userfeatures_dao.agent_id(user_id)
        else:
            agent_id = IdConverter.xid_to_id(agent_id)
        return agent_id

    def find_agent_exten(self, agent_id):
        user_ids = userfeatures_dao.find_by_agent_id(agent_id)
        line_ids = []
        for user_id in user_ids:
            line_ids.extend(self.line_features_dao.find_line_id_by_user_id(user_id))
        return [self.line_features_dao.number(line_id) for line_id in line_ids]

    def login(self, agent_id, exten, context):
        self.agent_executor.login(agent_id, exten, context)

    def logoff(self, agent_id):
        self.agent_executor.logoff(agent_id)

    def queueadd(self, queuename, agentid, paused=False, skills=''):
        interface = self.agent_features_dao.agent_interface(agentid)
        if interface is not None:
            self.agent_executor.queue_add(queuename, interface, paused, skills)

    def queueremove(self, queuename, agentid):
        interface = self.agent_features_dao.agent_interface(agentid)
        if interface is not None:
            self.agent_executor.queue_remove(queuename, interface)

    def queuepause_all(self, agentid):
        interface = self.agent_features_dao.agent_interface(agentid)
        if interface is not None:
            self.agent_executor.queues_pause(interface)

    def queueunpause_all(self, agentid):
        interface = self.agent_features_dao.agent_interface(agentid)
        if interface is not None:
            self.agent_executor.queues_unpause(interface)

    def queuepause(self, queuename, agentid):
        interface = self.agent_features_dao.agent_interface(agentid)
        if interface is not None:
            self.agent_executor.queue_pause(queuename, interface)

    def queueunpause(self, queuename, agentid):
        interface = self.agent_features_dao.agent_interface(agentid)
        if interface is not None:
            self.agent_executor.queue_unpause(queuename, interface)

    def set_presence(self, agentid, presence):
        interface = self.agent_features_dao.agent_interface(agentid)
        if interface is not None:
            self.agent_executor.log_presence(interface, presence)
