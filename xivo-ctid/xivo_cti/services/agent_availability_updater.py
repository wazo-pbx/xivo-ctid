# -*- coding: utf-8 -*-

# Copyright (C) 2007-2012  Avencall

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from xivo_cti import dao
from xivo_cti.scheduler import Scheduler
from xivo_cti.services.agent_status import AgentStatus

logger = logging.getLogger(__name__)


def parse_ami_login(ami_event, agent_availability_updater):
    agent_number = ami_event['Agent']
    agent_id = dao.agent.get_id_from_number(agent_number)
    agent_availability_updater.agent_logged_in(agent_id)


def parse_ami_logout(ami_event, agent_availability_updater):
    agent_number = ami_event['Agent']
    agent_id = dao.agent.get_id_from_number(agent_number)
    agent_availability_updater.agent_logged_out(agent_id)


def parse_ami_answered(ami_event, agent_availability_updater):
    agent_number = ami_event['Agent']
    agent_id = dao.agent.get_id_from_number(agent_number)
    agent_availability_updater.agent_answered(agent_id)


def parse_ami_call_completed(ami_event, agent_availability_updater):
    agent_number = ami_event['Agent']
    agent_wrapup = int(ami_event['WrapupTime'])
    agent_id = dao.agent.get_id_from_number(agent_number)
    agent_availability_updater.agent_call_completed(agent_id, agent_wrapup)


def parse_ami_paused(ami_event, agent_availability_updater):
    agent_number = ami_event['Agent']
    agent_id = dao.agent.get_id_from_number(agent_number)
    paused = ami_event['Paused'] == '1'
    if paused and dao.agent.is_completely_paused(agent_id):
        agent_availability_updater.agent_paused_all(agent_id)
    else:
        agent_availability_updater.agent_unpaused(agent_id)


class AgentAvailabilityUpdater(object):
    def __init__(self, innerdata_dao, notifier, scheduler=Scheduler()):
        self.innerdata_dao = innerdata_dao
        self.scheduler = scheduler
        self.notifier = notifier

    def agent_logged_in(self, agent_id):
        self.innerdata_dao.set_agent_availability(agent_id, AgentStatus.available)
        self.notifier.notify(agent_id)

    def agent_logged_out(self, agent_id):
        self.innerdata_dao.set_agent_availability(agent_id, AgentStatus.logged_out)
        self.notifier.notify(agent_id)

    def agent_answered(self, agent_id):
        self.innerdata_dao.set_agent_availability(agent_id, AgentStatus.unavailable)
        self.notifier.notify(agent_id)

    def agent_call_completed(self, agent_id, wrapup_time):
        if wrapup_time != 0:
            self.scheduler.schedule(wrapup_time,
                                    self.agent_wrapup_completed,
                                    agent_id)
        else:
            self.innerdata_dao.set_agent_availability(agent_id, AgentStatus.available)
            self.notifier.notify(agent_id)

    def agent_wrapup_completed(self, agent_id):
        self.innerdata_dao.set_agent_availability(agent_id, AgentStatus.available)
        self.notifier.notify(agent_id)

    def agent_paused_all(self, agent_id):
        self.innerdata_dao.set_agent_availability(agent_id, AgentStatus.unavailable)
        self.notifier.notify(agent_id)

    def agent_unpaused(self, agent_id):
        self.innerdata_dao.set_agent_availability(agent_id, AgentStatus.available)
        self.notifier.notify(agent_id)
