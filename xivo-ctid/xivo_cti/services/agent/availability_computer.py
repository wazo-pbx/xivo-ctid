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
from xivo_cti import dao
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.services.call.direction import CallDirection
from xivo_dao import agent_status_dao

logger = logging.getLogger(__name__)


class AgentAvailabilityComputer(object):

    def __init__(self, agent_availability_updater):
        self.updater = agent_availability_updater

    def compute(self, agent_id):
        if not agent_status_dao.is_agent_logged_in(agent_id):
            agent_status = AgentStatus.logged_out
        elif dao.agent.is_completely_paused(agent_id):
            agent_status = AgentStatus.unavailable
        elif dao.agent.on_wrapup(agent_id):
            agent_status = AgentStatus.unavailable
        elif dao.agent.on_call_acd(agent_id):
            agent_status = AgentStatus.unavailable
        else:
            agent_status = self._compute_non_acd_status(agent_id)

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
