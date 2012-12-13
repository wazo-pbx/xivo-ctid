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
# contracted with Avencall. See the LICENSE file at top of the source tree
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
from xivo_dao import agent_dao
from xivo_dao import line_dao
from xivo_dao import user_dao
from xivo_dao import queue_dao
from xivo_cti.exception import ExtensionInUseError

logger = logging.getLogger('Agent Manager')


class AgentServiceManager(object):

    def __init__(self, agent_executor, queue_member_manager):
        self.agent_executor = agent_executor
        self._queue_member_manager = queue_member_manager

    def on_cti_agent_login(self, user_id, agent_xid=None, agent_exten=None):
        agent_id = self._transform_agent_xid(user_id, agent_xid)
        if not agent_id:
            logger.info('%s not an agent (%s)', agent_xid, agent_exten)
            return 'error', {'error_string': 'agent_login_invalid_exten',
                             'class': 'ipbxcommand'}
        if not agent_exten:
            extens = self.find_agent_exten(agent_id)
            agent_exten = extens[0] if extens else None

        if not line_dao.is_phone_exten(agent_exten):
            logger.info('%s tried to login with wrong exten (%s)', agent_id, agent_exten)
            return 'error', {'error_string': 'agent_login_invalid_exten',
                             'class': 'ipbxcommand'}

        agent_context = agent_dao.agent_context(agent_id)
        try:
            self.login(agent_id, agent_exten, agent_context)
        except ExtensionInUseError:
            logger.warning('could not log agent %s on exten %s@%s: already in use',
                           agent_id, agent_exten, agent_context)
            return 'error', {'error_string': 'agent_login_exten_in_use',
                             'class': 'ipbxcommand'}

    def on_cti_agent_logout(self, user_id, agent_xid=None):
        agent_id = self._transform_agent_xid(user_id, agent_xid)
        if not agent_id:
            logger.info('%s not an agent', agent_xid)
            return 'error', {'error_string': 'agent_login_invalid_exten',
                             'class': 'ipbxcommand'}

        self.logoff(agent_id)

    def _transform_agent_xid(self, user_id, agent_id):
        if not agent_id or agent_id == 'agent:special:me':
            agent_id = user_dao.agent_id(user_id)
        else:
            agent_id = IdConverter.xid_to_id(agent_id)
        return agent_id

    def find_agent_exten(self, agent_id):
        user_ids = user_dao.find_by_agent_id(agent_id)
        line_ids = []
        for user_id in user_ids:
            line_ids.extend(line_dao.find_line_id_by_user_id(user_id))
        return [line_dao.number(line_id) for line_id in line_ids]

    def login(self, agent_id, exten, context):
        logger.info('Logging in agent %r', agent_id)
        self.agent_executor.login(agent_id, exten, context)

    def logoff(self, agent_id):
        logger.info('Logging off agent %r', agent_id)
        self.agent_executor.logoff(agent_id)

    def add_agent_to_queue(self, agent_id, queue_id):
        logger.info('Adding agent %r to queue %r', agent_id, queue_id)
        self.agent_executor.add_to_queue(agent_id, queue_id)

    def remove_agent_from_queue(self, agent_id, queue_id):
        logger.info('Removing agent %r from queue %r', agent_id, queue_id)
        self.agent_executor.remove_from_queue(agent_id, queue_id)

    def pause_agent_on_queue(self, agent_id, queue_id):
        logger.info('Pausing agent %r on queue %r', agent_id, queue_id)
        agent_interface = self._get_agent_interface(agent_id)
        if agent_interface:
            queue_name = queue_dao.queue_name(queue_id)
            self.agent_executor.pause_on_queue(agent_interface, queue_name)

    def pause_agent_on_all_queues(self, agent_id):
        logger.info('Pausing agent %r on all queues', agent_id)
        agent_interface = self._get_agent_interface(agent_id)
        if agent_interface:
            self.agent_executor.pause_on_all_queues(agent_interface)

    def unpause_agent_on_queue(self, agent_id, queue_id):
        logger.info('Unpausing agent %r on queue %r', agent_id, queue_id)
        agent_interface = self._get_agent_interface(agent_id)
        if agent_interface:
            queue_name = queue_dao.queue_name(queue_id)
            self.agent_executor.unpause_on_queue(agent_interface, queue_name)

    def unpause_agent_on_all_queues(self, agent_id):
        logger.info('Unpausing agent %r on all queues', agent_id)
        agent_interface = self._get_agent_interface(agent_id)
        if agent_interface:
            self.agent_executor.unpause_on_all_queues(agent_interface)

    def set_presence(self, agent_id, presence):
        agent_member_name = agent_dao.agent_interface(agent_id)
        if agent_member_name is not None:
            self.agent_executor.log_presence(agent_member_name, presence)

    def _get_agent_interface(self, agent_id):
        # convoluted way to get the agent interface (not the agent member name) of an agent
        # would be easier if the interface was kept in an "agent state" object instead
        # of only in the queue member state
        agent_number = agent_dao.agent_number(agent_id)
        queue_members = self._queue_member_manager.get_queue_members_by_agent_number(agent_number)
        if not queue_members:
            logger.warning('Could not get interface of agent %r: no queue members found',
                           agent_id)
            return None

        interface = queue_members[0].state.interface
        if not interface:
            logger.warning('Could not get interface of agent %r: no interface associated',
                           agent_id)
            return None

        return interface
