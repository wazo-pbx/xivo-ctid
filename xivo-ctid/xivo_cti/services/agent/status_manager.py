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
from xivo_cti.services.agent.status import AgentStatus

logger = logging.getLogger(__name__)


class QueueEventReceiver(object):

    STATUS_DEVICE_NOT_INUSE = 1
    STATUS_DEVICE_INUSE = 2

    def __init__(self, queue_member_notifier, agent_status_manager):
        self._queue_member_notifier = queue_member_notifier
        self._agent_status_manager = agent_status_manager

    def subscribe(self):
        self._queue_member_notifier.subscribe_to_queue_member_update(self.on_queue_member_update)

    def on_queue_member_update(self, queue_member):
        member_name = queue_member.member_name
        status = int(queue_member.state.status)
        self._update_status(member_name, status)

    def _update_status(self, member_name, status):
        agent_id = self._get_agent_id(member_name)
        if not agent_id:
            return

        if status == self.STATUS_DEVICE_INUSE:
            self._agent_status_manager.device_in_use(agent_id)
        elif status == self.STATUS_DEVICE_NOT_INUSE:
            self._agent_status_manager.device_not_in_use(agent_id)

    def _get_agent_id(self, member_name):
        try:
            return dao.agent.get_id_from_interface(member_name)
        except ValueError:
            return None  # Not an agent member name


class AgentStatusManager(object):

    def __init__(self, agent_availability_updater, scheduler):
        self._agent_availability_updater = agent_availability_updater
        self.scheduler = scheduler

    def agent_logged_in(self, agent_id):
        if dao.agent.is_completely_paused(agent_id):
            agent_status = AgentStatus.unavailable
        elif dao.agent.on_call_nonacd(agent_id):
            agent_status = AgentStatus.on_call_nonacd
        else:
            agent_status = AgentStatus.available

        self._agent_availability_updater.update(agent_id, agent_status)

    def agent_logged_out(self, agent_id):
        agent_status = AgentStatus.logged_out
        self._agent_availability_updater.update(agent_id, agent_status)

    def device_in_use(self, agent_id):
        if dao.agent.on_call_nonacd(agent_id):
            return
        dao.agent.set_on_call_nonacd(agent_id, True)
        if not dao.agent.is_logged(agent_id):
            return
        if dao.agent.on_wrapup(agent_id):
            return
        if dao.agent.is_completely_paused(agent_id):
            return
        if dao.agent.on_call_acd(agent_id):
            return
        self._agent_availability_updater.update(agent_id, AgentStatus.on_call_nonacd)

    def device_not_in_use(self, agent_id):
        if not dao.agent.on_call_nonacd(agent_id):
            return
        dao.agent.set_on_call_nonacd(agent_id, False)
        if not dao.agent.is_logged(agent_id):
            return
        if dao.agent.on_wrapup(agent_id):
            return
        if dao.agent.is_completely_paused(agent_id):
            return
        if dao.agent.on_call_acd(agent_id):
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
        if dao.agent.on_call_nonacd(agent_id):
            self._agent_availability_updater.update(agent_id, AgentStatus.on_call_nonacd)
        else:
            self._agent_availability_updater.update(agent_id, AgentStatus.available)

    def agent_paused_all(self, agent_id):
        if not dao.agent.is_logged(agent_id):
            return
        self._agent_availability_updater.update(agent_id, AgentStatus.unavailable)

    def agent_unpaused(self, agent_id):
        if not dao.agent.is_logged(agent_id):
            return
        if dao.agent.on_wrapup(agent_id):
            return
        if dao.agent.on_call_acd(agent_id):
            return
        if dao.agent.on_call_nonacd(agent_id):
            self._agent_availability_updater.update(agent_id, AgentStatus.on_call_nonacd)
        else:
            self._agent_availability_updater.update(agent_id, AgentStatus.available)