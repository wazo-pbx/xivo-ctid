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
from xivo_cti.ami import ami_callback_handler
from xivo_cti.services.agent_status import AgentStatus

logger = logging.getLogger("AMIAgentLogin")


class AMIAgentLoginLogoff(object):

    AGENTSTATUS_IDLE = 'AGENT_IDLE'
    AGENTSTATUS_ONCALL = 'AGENT_ONCALL'
    AGENTSTATUS_WHEN_LOGGED_IN = [AGENTSTATUS_IDLE, AGENTSTATUS_ONCALL]

    _instance = None

    def __init__(self):
        pass

    def _build_agent_id(self, agent_number):
        return 'Agent/%s' % agent_number

    def on_event_agent_login(self, event):
        agent_id = self._build_agent_id(event['AgentNumber'])
        self.queue_statistics_producer.on_agent_loggedon(agent_id)

    def on_event_agent_logoff(self, event):
        agent_id = self._build_agent_id(event['AgentNumber'])
        self.queue_statistics_producer.on_agent_loggedoff(agent_id)

    def on_event_agent_init(self, event):
        self._initialize_queue_statistics_producer(event)
        self._initialize_agents_status(event)

    def _initialize_queue_statistics_producer(self, event):
        if (event['Status'] in self.AGENTSTATUS_WHEN_LOGGED_IN):
            agent_id = self._build_agent_id(event['Agent'])
            self.queue_statistics_producer.on_agent_loggedon(agent_id)

    def _initialize_agents_status(self, event):
        agent_name = event['Agent']
        agent_id = self.agent_features_dao.agent_id(agent_name)
        agent_status_ami = event['Status']
        if agent_status_ami == self.AGENTSTATUS_IDLE:
            agent_status_cti = AgentStatus.available
        elif agent_status_ami == self.AGENTSTATUS_ONCALL:
            agent_status_cti = AgentStatus.unavailable
        else:
            agent_status_cti = AgentStatus.logged_out
        self.innerdata_dao.set_agent_availability(agent_id, agent_status_cti)

    @classmethod
    def register_callbacks(cls):
        callback_handler = ami_callback_handler.AMICallbackHandler.get_instance()
        ami_agent_login = cls.get_instance()
        callback_handler.register_userevent_callback('AgentLogin', ami_agent_login.on_event_agent_login)
        callback_handler.register_userevent_callback('AgentLogoff', ami_agent_login.on_event_agent_logoff)
        callback_handler.register_callback('Agents', ami_agent_login.on_event_agent_init)

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
