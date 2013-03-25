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

logger = logging.getLogger(__name__)


def parse_ami_answered(ami_event, agent_status_manager):
    agent_member_name = ami_event['MemberName']
    try:
        agent_id = dao.agent.get_id_from_interface(agent_member_name)
    except ValueError:
        pass  # Not an agent member name
    else:
        agent_status_manager.agent_in_use(agent_id)


def parse_ami_call_completed(ami_event, agent_status_manager):
    agent_member_name = ami_event['MemberName']
    wrapup = int(ami_event['WrapupTime'])

    try:
        agent_id = dao.agent.get_id_from_interface(agent_member_name)
    except ValueError:
        pass  # Not an agent member name
    else:
        agent_status_manager.agent_not_in_use(agent_id, wrapup)


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
            self._agent_status_manager.agent_in_use(agent_id)
        elif status == self.STATUS_DEVICE_NOT_INUSE:
            self._agent_status_manager.agent_not_in_use(agent_id)

    def _get_agent_id(self, member_name):
        try:
            return dao.agent.get_id_from_interface(member_name)
        except ValueError:
            return None  # Not an agent member name


class AgentStatusManager(object):

    def __init__(self, agent_availability_updater):
        self._agent_availability_updater = agent_availability_updater

    def agent_in_use(self, agent_id):
        if dao.agent.on_call(agent_id):
            return

        dao.agent.set_on_call(agent_id, True)
        self._agent_availability_updater.agent_in_use(agent_id)

    def agent_not_in_use(self, agent_id, wrapup=0):
        if not dao.agent.on_call(agent_id):
            return

        dao.agent.set_on_call(agent_id, False)
        self._agent_availability_updater.agent_call_completed(agent_id, wrapup)
