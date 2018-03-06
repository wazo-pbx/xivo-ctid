# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging
from xivo_cti.ami import ami_callback_handler

logger = logging.getLogger("AMIAgentLogin")


class AMIAgentLoginLogoff(object):

    _instance = None

    def _build_agent_id(self, agent_number):
        return 'Agent/%s' % agent_number

    def on_event_agent_login(self, event):
        agent_id = self._build_agent_id(event['AgentNumber'])
        self.queue_statistics_producer.on_agent_loggedon(agent_id)

    def on_event_agent_logoff(self, event):
        agent_id = self._build_agent_id(event['AgentNumber'])
        self.queue_statistics_producer.on_agent_loggedoff(agent_id)

    @classmethod
    def register_callbacks(cls):
        callback_handler = ami_callback_handler.AMICallbackHandler.get_instance()
        ami_agent_login = cls.get_instance()
        callback_handler.register_userevent_callback('AgentLogin', ami_agent_login.on_event_agent_login)
        callback_handler.register_userevent_callback('AgentLogoff', ami_agent_login.on_event_agent_logoff)

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
