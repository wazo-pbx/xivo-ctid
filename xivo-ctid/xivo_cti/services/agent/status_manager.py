# -*- coding: UTF-8 -*-

# Copyright (C) 2013  Avencall
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
from xivo_cti.dao.agent_dao import AgentCallStatus, AgentNonACDStatus
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.services.call.direction import CallDirection

logger = logging.getLogger(__name__)


class AgentStatusManager(object):

    def __init__(self, agent_availability_updater, scheduler):
        self._agent_availability_updater = agent_availability_updater
        self.scheduler = scheduler

    def agent_logged_in(self, agent_id):
        if dao.agent.is_completely_paused(agent_id):
            agent_status = AgentStatus.unavailable
        elif dao.agent.call_status(agent_id) == AgentCallStatus.incoming_call_nonacd:
            agent_status = AgentStatus.on_call_nonacd_incoming
        elif dao.agent.call_status(agent_id) == AgentCallStatus.outgoing_call_nonacd:
            agent_status = AgentStatus.on_call_nonacd_outgoing
        else:
            agent_status = AgentStatus.available

        self._agent_availability_updater.update(agent_id, agent_status)

    def agent_logged_out(self, agent_id):
        dao.agent.set_on_wrapup(agent_id, False)
        agent_status = AgentStatus.logged_out
        self._agent_availability_updater.update(agent_id, agent_status)

    def device_in_use(self, agent_id, direction):
        if dao.agent.call_status(agent_id) in [AgentCallStatus.incoming_call_nonacd,
                                               AgentCallStatus.outgoing_call_nonacd]:
            return
        if direction == CallDirection.incoming:
            dao.agent.set_on_call_nonacd(agent_id, AgentNonACDStatus.incoming)
        elif direction == CallDirection.outgoing:
            dao.agent.set_on_call_nonacd(agent_id, AgentNonACDStatus.outgoing)
        if not dao.agent.is_logged(agent_id):
            return
        if dao.agent.on_wrapup(agent_id):
            return
        if dao.agent.is_completely_paused(agent_id):
            return
        if dao.agent.call_status(agent_id) == AgentCallStatus.call_acd:
            return
        if direction == CallDirection.incoming:
            self._agent_availability_updater.update(agent_id, AgentStatus.on_call_nonacd_incoming)
        elif direction == CallDirection.outgoing:
            self._agent_availability_updater.update(agent_id, AgentStatus.on_call_nonacd_outgoing)

    def device_not_in_use(self, agent_id):
        if dao.agent.call_status(agent_id) == AgentCallStatus.no_call:
            return
        dao.agent.set_on_call_nonacd(agent_id, False)
        if not dao.agent.is_logged(agent_id):
            return
        if dao.agent.on_wrapup(agent_id):
            return
        if dao.agent.is_completely_paused(agent_id):
            return
        if dao.agent.call_status(agent_id) == AgentCallStatus.call_acd:
            return
        self._agent_availability_updater.update(agent_id, AgentStatus.available)

    def acd_call_start(self, agent_id):
        dao.agent.set_on_call_acd(agent_id, True)
        self._agent_availability_updater.update(agent_id, AgentStatus.unavailable)

    def acd_call_end(self, agent_id):
        dao.agent.set_on_call_acd(agent_id, False)
        if dao.agent.is_completely_paused(agent_id):
            return
        self._agent_availability_updater.update(agent_id, AgentStatus.available)

    def agent_in_wrapup(self, agent_id, wrapup_time):
        dao.agent.set_on_call_acd(agent_id, False)
        dao.agent.set_on_wrapup(agent_id, True)
        self.scheduler.schedule(wrapup_time,
                                self.agent_wrapup_completed,
                                agent_id)

    def agent_wrapup_completed(self, agent_id):
        dao.agent.set_on_wrapup(agent_id, False)
        if dao.agent.is_completely_paused(agent_id):
            return
        if not dao.agent.is_logged(agent_id):
            return
        agent_call_status = dao.agent.call_status(agent_id)
        if agent_call_status == AgentCallStatus.no_call:
            self._agent_availability_updater.update(agent_id, AgentStatus.available)
        elif agent_call_status == AgentCallStatus.incoming_call_nonacd:
            self._agent_availability_updater.update(agent_id, AgentStatus.on_call_nonacd_incoming)
        elif agent_call_status == AgentCallStatus.outgoing_call_nonacd:
            self._agent_availability_updater.update(agent_id, AgentStatus.on_call_nonacd_outgoing)

    def agent_paused_all(self, agent_id):
        if not dao.agent.is_logged(agent_id):
            return
        self._agent_availability_updater.update(agent_id, AgentStatus.unavailable)

    def agent_unpaused(self, agent_id):
        if not dao.agent.is_logged(agent_id):
            return
        if dao.agent.on_wrapup(agent_id):
            return
        agent_call_status = dao.agent.call_status(agent_id)
        if agent_call_status == AgentCallStatus.call_acd:
            return
        if agent_call_status == AgentCallStatus.no_call:
            self._agent_availability_updater.update(agent_id, AgentStatus.available)
        elif agent_call_status == AgentCallStatus.incoming_call_nonacd:
            self._agent_availability_updater.update(agent_id, AgentStatus.on_call_nonacd_incoming)
        elif agent_call_status == AgentCallStatus.outgoing_call_nonacd:
            self._agent_availability_updater.update(agent_id, AgentStatus.on_call_nonacd_outgoing)
