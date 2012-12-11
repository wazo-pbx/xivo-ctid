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

from xivo_agent.ctl import error
from xivo_agent.exception import AgentClientError


class AgentExecutor(object):

    def __init__(self, agent_client, interface_ami):
        self._agent_client = agent_client
        self.ami = interface_ami.amiclass

    def queue_add(self, queuename, interface, paused=False, skills=''):
        self.ami.queueadd(queuename, interface, paused, skills)

    def queue_remove(self, queuename, interface):
        self.ami.queueremove(queuename, interface)

    def queue_pause(self, queuename, interface):
        self.ami.queuepause(queuename, interface, 'True')

    def queue_unpause(self, queuename, interface):
        self.ami.queuepause(queuename, interface, 'False')

    def queues_pause(self, interface):
        self.ami.queuepauseall(interface, 'True')

    def queues_unpause(self, interface):
        self.ami.queuepauseall(interface, 'False')

    def login(self, agent_id, exten, context):
        self._agent_client.login_agent(agent_id, exten, context)

    def logoff(self, agent_id):
        try:
            self._agent_client.logoff_agent(agent_id)
        except AgentClientError as e:
            if e.error != error.NOT_LOGGED:
                raise

    def log_presence(self, agent_interface, presence):
        self.ami.queuelog('NONE', 'PRESENCE', interface=agent_interface, message=presence)
