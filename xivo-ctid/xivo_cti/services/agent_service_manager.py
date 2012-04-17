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

    def log_agent(self, user_id, agent_id=None, agent_exten=None):
        if not agent_id or agent_id == 'agent:special:me':
            agent_id = self.user_features_dao.agent_id(user_id)
        agent_id = IdConverter.xid_to_id(agent_id)
        if agent_exten and not self.line_features_dao.is_phone_exten(agent_exten):
            logger.info('%s tried to login with wrong exten (%s)', agent_id, agent_exten)
            return 'error', {'error_string': 'invalid_exten',
                             'class': 'ipbxcommand'}
        if not agent_exten:
            extens = self.find_agent_exten(agent_id)
            agent_exten = extens[0] if len(extens) else None
        self.agent_call_back_login(self.agent_features_dao.agent_number(agent_id),
                                   agent_exten,
                                   self.agent_features_dao.agent_context(agent_id),
                                   self.agent_features_dao.agent_ackcall(agent_id) != 'no')

    def find_agent_exten(self, agent_id):
        user_ids = self.user_features_dao.find_by_agent_id(agent_id)
        line_ids = []
        for user_id in user_ids:
            line_ids.extend(self.line_features_dao.find_by_user(user_id))
        return [self.line_features_dao.number(line_id) for line_id in line_ids]

    def agent_call_back_login(self, number, exten, context, ackcall):
        self.ami.agentcallbacklogin(number, exten, context, ackcall)

    def queuepause_all(self, agentid):
        interface = self.agent_features_dao.agent_interface(agentid)
        self.agent_service_executor.queues_pause(interface)
