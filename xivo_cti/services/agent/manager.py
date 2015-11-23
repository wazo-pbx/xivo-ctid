# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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
from xivo_cti.tools.idconverter import IdConverter

from xivo_dao.helpers.db_utils import session_scope
from xivo_dao.resources.user import dao as user_dao
from xivo_dao import agent_dao
from xivo_dao import user_line_dao
from xivo_dao import agent_status_dao
from xivo_dao import queue_dao

from xivo_cti.exception import ExtensionInUseError, NoSuchExtensionError

logger = logging.getLogger('Agent Manager')


class AgentServiceManager(object):

    def __init__(self, agent_executor, ami_class):
        self.agent_executor = agent_executor
        self.ami = ami_class

    def on_cti_agent_login(self, user_id, agent_xid=None, agent_exten=None):
        agent_id = self._transform_agent_xid(user_id, agent_xid)
        if not agent_id:
            logger.info('%s not an agent (%s)', agent_xid, agent_exten)
            return 'error', {'error_string': 'agent_login_invalid_exten',
                             'class': 'ipbxcommand'}
        if not agent_exten:
            extens = self.find_agent_exten(agent_id)
            agent_exten = extens[0] if extens else None

        with session_scope():
            if not user_line_dao.is_phone_exten(agent_exten):
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
        except NoSuchExtensionError:
            logger.warning('could not log agent %s on exten %s@%s: no such extension',
                           agent_id, agent_exten, agent_context)
            return 'error', {'error_string': 'agent_login_invalid_exten',
                             'class': 'ipbxcommand'}

    def on_cti_agent_logout(self, user_id, agent_xid=None):
        agent_id = self._transform_agent_xid(user_id, agent_xid)
        if not agent_id:
            logger.info('%s not an agent', agent_xid)
            return 'error', {'error_string': 'agent_login_invalid_exten',
                             'class': 'ipbxcommand'}

        self.logoff(agent_id)

    def on_cti_listen(self, user_id, agent_xid):
        agent_id = self._transform_agent_xid(user_id, agent_xid)
        agent_state_interface = self._get_agent_state_interface(agent_id)
        if agent_state_interface:
            try:
                user_state_interface = self._get_user_state_interface(user_id)
            except LookupError:
                logger.warning('Could not listen to agent: user %s has no line', user_id)
            else:
                self.ami.sendcommand(
                    'Originate',
                    [('Channel', user_state_interface),
                     ('Application', 'ChanSpy'),
                     ('Data', '%s,bds' % agent_state_interface),
                     ('CallerID', u'Listen/Écouter'),
                     ('Async', 'true')]
                )

    def _transform_agent_xid(self, user_id, agent_xid):
        if not agent_xid or agent_xid == 'agent:special:me':
            with session_scope():
                user = user_dao.find(user_id)
                if user:
                    return user.agentid
        else:
            return IdConverter.xid_to_id(agent_xid)

    def find_agent_exten(self, agent_id):
        with session_scope():
            line_ids = []
            users = user_dao.find_all_by(agentid=agent_id)
            for user in users:
                line_ids.extend(user_line_dao.find_line_id_by_user_id(user.id))
            return [user_line_dao.get_main_exten_by_line_id(line_id) for line_id in line_ids]

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
            with session_scope():
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
            with session_scope():
                queue_name = queue_dao.queue_name(queue_id)
            self.agent_executor.unpause_on_queue(agent_interface, queue_name)

    def unpause_agent_on_all_queues(self, agent_id):
        logger.info('Unpausing agent %r on all queues', agent_id)
        agent_interface = self._get_agent_interface(agent_id)
        if agent_interface:
            self.agent_executor.unpause_on_all_queues(agent_interface)

    def set_presence(self, agent_id, presence):
        with session_scope():
            agent_member_name = agent_dao.find_agent_interface(agent_id)
        if agent_member_name is not None:
            self.agent_executor.log_presence(agent_member_name, presence)

    def _get_agent_interface(self, agent_id):
        agent_status = self._get_agent_status(agent_id)
        if agent_status:
            return agent_status.interface
        else:
            return None

    def _get_agent_state_interface(self, agent_id):
        agent_status = self._get_agent_status(agent_id)
        if agent_status:
            return agent_status.state_interface
        else:
            return None

    def _get_agent_status(self, agent_id):
        with session_scope():
            agent_status = agent_status_dao.get_status(agent_id)
        if agent_status:
            return agent_status
        else:
            logger.warning('Could not get status of agent %r: not logged/no such agent', agent_id)
            return None

    def _get_user_state_interface(self, user_id):
        with session_scope():
            user_line = user_line_dao.get_line_identity_by_user_id(user_id)
            user = user_dao.find(user_id)
            connected_agent_id = user.agentid if user else None

        if connected_agent_id is None:
            return user_line

        loggedon_state_interface = self._get_agent_state_interface(connected_agent_id)
        if loggedon_state_interface is None:
            loggedon_state_interface = user_line
        return loggedon_state_interface
