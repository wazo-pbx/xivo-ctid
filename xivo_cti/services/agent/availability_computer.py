# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_cti import dao
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.services.call.direction import CallDirection

from xivo_dao.helpers.db_utils import session_scope
from xivo_dao import agent_status_dao

logger = logging.getLogger(__name__)


class AgentAvailabilityComputer(object):

    def __init__(self, agent_availability_updater):
        self.updater = agent_availability_updater

    def compute(self, agent_id):
        with session_scope():
            agent_logged_in = agent_status_dao.is_agent_logged_in(agent_id)

        if not agent_logged_in:
            agent_status = AgentStatus.logged_out
        elif dao.agent.on_call_acd(agent_id):
            agent_status = AgentStatus.unavailable
        elif dao.agent.on_call_nonacd(agent_id):
            agent_status = self._compute_non_acd_status(agent_id)
        elif dao.agent.is_completely_paused(agent_id):
            agent_status = AgentStatus.unavailable
        elif dao.agent.on_wrapup(agent_id):
            agent_status = AgentStatus.unavailable
        else:
            agent_status = AgentStatus.available

        self.updater.update(agent_id, agent_status)

    def _compute_non_acd_status(self, agent_id):
        call_status = dao.agent.nonacd_call_status(agent_id)
        if call_status is None:
            agent_status = AgentStatus.available
        elif call_status.is_internal:
            if call_status.direction == CallDirection.incoming:
                agent_status = AgentStatus.on_call_nonacd_incoming_internal
            else:
                agent_status = AgentStatus.on_call_nonacd_outgoing_internal
        else:
            if call_status.direction == CallDirection.incoming:
                agent_status = AgentStatus.on_call_nonacd_incoming_external
            else:
                agent_status = AgentStatus.on_call_nonacd_outgoing_external

        return agent_status
