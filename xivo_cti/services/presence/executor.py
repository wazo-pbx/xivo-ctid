# -*- coding: utf-8 -*-
# Copyright (C) 2007-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_cti import dao
from xivo_cti import config

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

    def __init__(self, user_service_manager, agent_service_manager):
        self.user_service_manager = user_service_manager
        self.agent_service_manager = agent_service_manager

    def execute_actions(self, user_id, user_uuid, auth_token, presence):
        user_profile = dao.user.get_cti_profile_id(user_id)
        presence_group_name = config['profiles'][user_profile]['userstatus']
        presence_group = config['userstatus'][presence_group_name]

        if presence not in presence_group:
            raise ValueError('Unknown service %s' % presence)

        list_action = presence_group[presence].get('actions', {})

        for action_name, action_param in list_action.iteritems():
            if action_name in self.services_actions_list:
                self._launch_presence_service(user_id, user_uuid, auth_token, action_name, action_param == 'true')
            elif action_name in self.queues_actions_list:
                self._launch_presence_queue(user_id, action_name)

    def _launch_presence_queue(self, user_id, action_name):
        agentid = dao.user.get_agent_id(user_id)
        if agentid:
            if action_name == 'queuepause_all':
                self.agent_service_manager.pause_agent_on_all_queues(agentid)
            elif action_name == 'queueunpause_all':
                self.agent_service_manager.unpause_agent_on_all_queues(agentid)
            else:
                raise NotImplementedError(action_name)

    def _launch_presence_service(self, user_id, user_uuid, auth_token, action_name, params):
        if action_name == 'agentlogoff':
            agentid = dao.user.get_agent_id(user_id)
            if agentid:
                self.agent_service_manager.logoff(agentid)
        elif action_name == 'enablednd':
            self.user_service_manager.set_dnd(user_uuid, auth_token, params)
        else:
            raise NotImplementedError(action_name)
