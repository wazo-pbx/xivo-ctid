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


class AgentExecutor(object):

    def __init__(self):
        pass

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

    def logoff(self, number):
        self.ami.agentlogoff(number)

    def agentcallbacklogin(self, number, exten, context):
        self.ami.agentcallbacklogin(number, exten, context)

    def log_presence(self, agent_interface, presence):
        self.ami.queuelog('NONE', 'PRESENCE', interface=agent_interface, message=presence)
