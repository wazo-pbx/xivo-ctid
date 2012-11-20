# vim: set fileencoding=utf-8 :
# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
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

logger = logging.getLogger('Agent Manager')


class AgentServiceManager(object):

    def __init__(self, agent_executor):
        self.agent_executor = agent_executor

    def log_agent(self, user_id, agent_id=None, agent_exten=None):
        if not agent_id or agent_id == 'agent:special:me':
            agent_id = self.user_features_dao.agent_id(user_id)
        agent_id = IdConverter.xid_to_id(agent_id)

        if not agent_id:
            logger.info('%s not an agent (%s)', agent_id, agent_exten)
            return 'error', {'error_string': 'invalid_exten',
                             'class': 'ipbxcommand'}
        if not agent_exten:
            extens = self.find_agent_exten(agent_id)
            agent_exten = extens[0] if extens else None

        if not self.line_features_dao.is_phone_exten(agent_exten):
            logger.info('%s tried to login with wrong exten (%s)', agent_id, agent_exten)
            return 'error', {'error_string': 'invalid_exten',
                             'class': 'ipbxcommand'}

        self.agent_call_back_login(self.agent_features_dao.agent_number(agent_id),
                                   agent_exten,
                                   self.agent_features_dao.agent_context(agent_id))

    def logoff(self, agent_id):
        number = self.agent_features_dao.agent_number(agent_id)
        if number is not None:
            self.agent_executor.logoff(number)

    def find_agent_exten(self, agent_id):
        user_ids = self.user_features_dao.find_by_agent_id(agent_id)
        line_ids = []
        for user_id in user_ids:
            line_ids.extend(self.line_features_dao.find_line_id_by_user_id(user_id))
        return [self.line_features_dao.number(line_id) for line_id in line_ids]

    def agent_call_back_login(self, number, exten, context):
        self.agent_executor.agentcallbacklogin(number, exten, context)

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
