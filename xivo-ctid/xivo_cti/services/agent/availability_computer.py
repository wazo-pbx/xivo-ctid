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

from xivo_cti import dao
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.dao.agent_dao import AgentNonACDStatus
from xivo_dao import agent_status_dao


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
            call_status = dao.agent.on_call_nonacd(agent_id)
            if call_status == AgentNonACDStatus.no_call:
                agent_status = AgentStatus.available
            elif call_status == AgentNonACDStatus.incoming:
                agent_status = AgentStatus.on_call_nonacd_incoming
            else:
                agent_status = AgentStatus.on_call_nonacd_outgoing

        self.updater.update(agent_id, agent_status)
