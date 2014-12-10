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

from xivo_cti import dao
from xivo_cti import config
from xivo_dao import user_dao

logger = logging.getLogger('PresenceServiceExecutor')


class PresenceServiceExecutor(object):
    services_actions_list = ['enablevoicemail',
                             'callrecord',
                             'incallfilter',
                             'enablednd',
                             'enableunc',
                             'enablebusy',
                             'enablerna',
                             'agentlogoff']

    queues_actions_list = ['queueadd',
                           'queueremove',
                           'queuepause',
                           'queueunpause',
                           'queuepause_all',
                           'queueunpause_all']

    def __init__(self,
                 user_service_manager,
                 agent_service_manager,
                 innerdata):
        self.user_service_manager = user_service_manager
        self.agent_service_manager = agent_service_manager
        self._innerdata = innerdata

    def execute_actions(self, user_id, presence):
        user_profile = dao.user.get_cti_profile_id(user_id)
        presence_group_name = config['profiles'][user_profile]['userstatus']
        presence_group = config['userstatus'][presence_group_name]

        if presence not in presence_group:
            raise ValueError('Unknown service %s' % presence)

        list_action = presence_group[presence].get('actions', {})

        for action_name, action_param in list_action.iteritems():
            if action_name in self.services_actions_list:
                self._launch_presence_service(user_id, action_name, action_param == 'true')
            elif action_name in self.queues_actions_list:
                self._launch_presence_queue(user_id, action_name)

    def _launch_presence_queue(self, user_id, action_name):
        agentid = user_dao.agent_id(user_id)
        if agentid:
            if action_name == 'queuepause_all':
                self.agent_service_manager.pause_agent_on_all_queues(agentid)
            elif action_name == 'queueunpause_all':
                self.agent_service_manager.unpause_agent_on_all_queues(agentid)
            else:
                raise NotImplementedError(action_name)

    def _launch_presence_service(self, user_id, action_name, params):
        if action_name == 'agentlogoff':
            agentid = user_dao.agent_id(user_id)
            if agentid:
                self.agent_service_manager.logoff(agentid)
        elif action_name == 'enablednd':
            self.user_service_manager.set_dnd(user_id, params)
        else:
            raise NotImplementedError(action_name)
