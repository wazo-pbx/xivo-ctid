# -*- coding: utf-8 -*-

import logging

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

    def execute_actions(self, user_id, presence):
        actions = self._innerdata.get_user_permissions('userstatus', user_id)

        if presence not in actions:
            raise ValueError('Unknown service %s' % presence)

        list_action = actions[presence].get('actions', {})

        for action_name, action_param in list_action.iteritems():
            if action_name in self.services_actions_list:
                self._launch_presence_service(user_id, action_name, action_param == 'true')
            elif action_name in self.queues_actions_list:
                self._launch_presence_queue(user_id, action_name)

    def _launch_presence_queue(self, user_id, action_name):
        agentid = self.user_features_dao.agent_id(user_id)
        if agentid:
            if action_name == 'queuepause_all':
                self.agent_service_manager.queuepause_all(agentid)
            elif action_name == 'queueunpause_all':
                self.agent_service_manager.queueunpause_all(agentid)
            else:
                raise NotImplementedError(action_name)

    def _launch_presence_service(self, user_id, action_name, params):
        if action_name == 'agentlogoff':
            agentid = self.user_features_dao.agent_id(user_id)
            if agentid:
                self.agent_service_manager.logoff(agentid)
        elif action_name == 'enablednd':
            self.user_service_manager.set_dnd(user_id, params)
        else:
            raise NotImplementedError(action_name)
