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
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti import dao
from xivo_cti.exception import NoSuchAgentException

logger = logging.getLogger(__name__)


def parse_ami_login(ami_event, agent_availability_updater):
    agent_id = int(ami_event['AgentID'])
    agent_availability_updater.agent_logged_in(agent_id)


def parse_ami_logout(ami_event, agent_availability_updater):
    agent_id = int(ami_event['AgentID'])
    agent_availability_updater.agent_logged_out(agent_id)


def parse_ami_paused(ami_event, agent_availability_updater):
    agent_member_name = ami_event['MemberName']
    paused = ami_event['Paused'] == '1'
    try:
        agent_id = dao.agent.get_id_from_interface(agent_member_name)
    except ValueError:
        pass  # Not an agent member name
    else:
        if paused and dao.agent.is_completely_paused(agent_id):
            agent_availability_updater.agent_paused_all(agent_id)
        else:
            agent_availability_updater.agent_unpaused(agent_id)


class AgentAvailabilityUpdater(object):

    def __init__(self, agent_availability_notifier, scheduler):
        self.dao = dao
        self.scheduler = scheduler
        self.notifier = agent_availability_notifier

    def agent_logged_in(self, agent_id):
        if dao.agent.is_completely_paused(agent_id):
            self.dao.innerdata.set_agent_availability(agent_id, AgentStatus.unavailable)
        else:
            self.dao.innerdata.set_agent_availability(agent_id, AgentStatus.available)
        self.notifier.notify(agent_id)

    def agent_logged_out(self, agent_id):
        try:
            self.dao.innerdata.set_agent_availability(agent_id, AgentStatus.logged_out)
        except NoSuchAgentException:
            logger.info('Tried to logout an unknown agent')
        else:
            self.notifier.notify(agent_id)

    def agent_in_use(self, agent_id):
        self.dao.innerdata.set_agent_availability(agent_id, AgentStatus.unavailable)
        self.notifier.notify(agent_id)

    def agent_not_in_use(self, agent_id):
        if dao.agent.is_completely_paused(agent_id):
            return
        if not dao.agent.is_logged(agent_id):
            return
        if dao.agent.on_wrapup(agent_id):
            return
        self.dao.innerdata.set_agent_availability(agent_id, AgentStatus.available)
        self.notifier.notify(agent_id)

    def agent_in_wrapup(self, agent_id, wrapup_time):
        self.scheduler.schedule(wrapup_time,
                                self.agent_wrapup_completed,
                                agent_id)

    def agent_wrapup_completed(self, agent_id):
        dao.agent.set_on_wrapup(agent_id, False)
        if dao.agent.is_completely_paused(agent_id):
            return
        if not dao.agent.is_logged(agent_id):
            return
        if dao.agent.on_call(agent_id):
            return
        self.dao.innerdata.set_agent_availability(agent_id, AgentStatus.available)
        self.notifier.notify(agent_id)

    def agent_paused_all(self, agent_id):
        if not dao.agent.is_logged(agent_id):
            return
        self.dao.innerdata.set_agent_availability(agent_id, AgentStatus.unavailable)
        self.notifier.notify(agent_id)

    def agent_unpaused(self, agent_id):
        if not dao.agent.is_logged(agent_id):
            return
        if dao.agent.on_call(agent_id):
            return
        if dao.agent.on_wrapup(agent_id):
            return
        self.dao.innerdata.set_agent_availability(agent_id, AgentStatus.available)
        self.notifier.notify(agent_id)
