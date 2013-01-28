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


def parse_ami_answered(ami_event, agent_on_call_updater):
    agent_member_name = ami_event['MemberName']
    try:
        agent_id = dao.agent.get_id_from_interface(agent_member_name)
    except ValueError:
        pass  # Not an agent member name
    else:
        agent_on_call_updater.answered_call(agent_id)


def parse_ami_call_completed(ami_event, agent_on_call_updater):
    agent_member_name = ami_event['MemberName']
    try:
        agent_id = dao.agent.get_id_from_interface(agent_member_name)
    except ValueError:
        pass  # Not an agent member name
    else:
        agent_on_call_updater.call_completed(agent_id)


class AgentOnCallUpdater(object):

    def __init__(self):
        pass

    def answered_call(self, agent_id):
        dao.agent.set_on_call(agent_id, True)

    def call_completed(self, agent_id):
        dao.agent.set_on_call(agent_id, False)
