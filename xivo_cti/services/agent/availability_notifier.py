# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter
from xivo_cti import dao

logger = logging.getLogger(__name__)


class AgentAvailabilityNotifier(object):

    def __init__(self, cti_server):
        self.cti_server = cti_server

    def notify(self, agent_id):
        agent_status = dao.agent.agent_status(agent_id)
        cti_message = CTIMessageFormatter.update_agent_status(agent_id, agent_status)
        self.cti_server.send_cti_event(cti_message)
