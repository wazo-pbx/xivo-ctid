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
from xivo_bus.resources.agent import error
from xivo_bus.resources.agent.exception import AgentClientError
from xivo_cti.exception import ExtensionInUseError, NoSuchExtensionError

logger = logging.getLogger(__name__)


class AgentExecutor(object):

    def __init__(self, agent_client, ami_class):
        self._agent_client = agent_client
        self.ami = ami_class

    def login(self, agent_id, exten, context):
        try:
            self._agent_client.login_agent(agent_id, exten, context)
        except AgentClientError as e:
            if e.error == error.ALREADY_IN_USE:
                raise ExtensionInUseError()
            elif e.error == error.ALREADY_LOGGED:
                logger.info('Agent with ID %s already logged', agent_id)
            elif e.error == error.NO_SUCH_EXTEN:
                raise NoSuchExtensionError()
            else:
                raise

    def logoff(self, agent_id):
        try:
            self._agent_client.logoff_agent(agent_id)
        except AgentClientError as e:
            if e.error != error.NOT_LOGGED:
                raise

    def add_to_queue(self, agent_id, queue_id):
        self._agent_client.add_agent_to_queue(agent_id, queue_id)

    def remove_from_queue(self, agent_id, queue_id):
        self._agent_client.remove_agent_from_queue(agent_id, queue_id)

    def pause_on_queue(self, agent_interface, queue_name):
        self.ami.queuepause(queue_name, agent_interface, 'True')

    def pause_on_all_queues(self, agent_interface):
        self.ami.queuepauseall(agent_interface, 'True')

    def unpause_on_queue(self, agent_interface, queue_name):
        self.ami.queuepause(queue_name, agent_interface, 'False')

    def unpause_on_all_queues(self, agent_interface):
        self.ami.queuepauseall(agent_interface, 'False')

    def log_presence(self, agent_member_name, presence):
        self.ami.queuelog('NONE', 'PRESENCE', interface=agent_member_name, message=presence)
