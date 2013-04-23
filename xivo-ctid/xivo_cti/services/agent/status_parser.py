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


class AgentStatusParser(object):

    def __init__(self):
        pass

    def parse_ami_login(self, ami_event, agent_status_manager):
        agent_id = int(ami_event['AgentID'])
        agent_status_manager.agent_logged_in(agent_id)

    def parse_ami_logout(self, ami_event, agent_status_manager):
        agent_id = int(ami_event['AgentID'])
        agent_status_manager.agent_logged_out(agent_id)

    def parse_ami_paused(self, ami_event, agent_status_manager):
        agent_member_name = ami_event['MemberName']
        paused = ami_event['Paused'] == '1'
        try:
            agent_id = dao.agent.get_id_from_interface(agent_member_name)
        except ValueError:
            pass  # Not an agent member name
        else:
            if paused and dao.agent.is_completely_paused(agent_id):
                agent_status_manager.agent_paused_all(agent_id)
            else:
                agent_status_manager.agent_unpaused(agent_id)

    def parse_ami_acd_call_start(self, ami_event, agent_status_manager):
        agent_member_name = ami_event['MemberName']
        try:
            agent_id = dao.agent.get_id_from_interface(agent_member_name)
        except ValueError:
            pass  # Not an agent member name
        else:
            agent_status_manager.acd_call_start(agent_id)

    def parse_ami_acd_call_end(self, ami_event, agent_status_manager):
        wrapup = int(ami_event['WrapupTime'])
        agent_member_name = ami_event['MemberName']
        try:
            agent_id = dao.agent.get_id_from_interface(agent_member_name)
        except ValueError:
            pass  # Not an agent member name
        else:
            if wrapup > 0:
                agent_status_manager.agent_in_wrapup(agent_id, wrapup)
            else:
                agent_status_manager.acd_call_end(agent_id)
