# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_agentd_client import error
from xivo_cti.exception import ExtensionInUseError, NoSuchExtensionError

logger = logging.getLogger(__name__)


class AgentExecutor(object):

    def __init__(self, agentd_client, ami_class):
        self._agentd_client = agentd_client
        self.ami = ami_class

    def login(self, agent_id, exten, context):
        try:
            self._agentd_client.agents.login_agent(agent_id, exten, context)
        except error.AgentdClientError as e:
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
            self._agentd_client.agents.logoff_agent(agent_id)
        except error.AgentdClientError as e:
            if e.error != error.NOT_LOGGED:
                raise

    def add_to_queue(self, agent_id, queue_id):
        self._agentd_client.agents.add_agent_to_queue(agent_id, queue_id)

    def remove_from_queue(self, agent_id, queue_id):
        self._agentd_client.agents.remove_agent_from_queue(agent_id, queue_id)

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
