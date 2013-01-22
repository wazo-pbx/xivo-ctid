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

from xivo_cti.services.agent.status import AgentStatus

logger = logging.getLogger(__name__)


class AgentDAO(object):

    def __init__(self, innerdata, queue_member_manager):
        self.innerdata = innerdata
        self._queue_member_manager = queue_member_manager

    def get_id_from_interface(self, agent_interface):
        first, agent_number = agent_interface.split('/', 1)
        if first != 'Agent':
            raise ValueError('%s is not an agent interface' % agent_interface)
        return self.get_id_from_number(agent_number)

    def get_id_from_number(self, agent_number):
        agent_list = self.innerdata.xod_config['agents'].keeplist
        for (agent_id, agent) in agent_list.iteritems():
            if agent['number'] == agent_number:
                return int(agent_id)

    def get_interface_from_id(self, agent_id):
        agent_list = self.innerdata.xod_config['agents'].keeplist
        agent_number = agent_list[str(agent_id)]['number']
        return 'Agent/%s' % agent_number

    def is_completely_paused(self, agent_id):
        agent_interface = self.get_interface_from_id(agent_id)

        agent_membership_count = self._queue_member_manager.get_queue_count_by_member_name(agent_interface)
        if agent_membership_count == 0:
            return False

        paused_count = self._queue_member_manager.get_paused_count_by_member_name(agent_interface)
        return paused_count == agent_membership_count

    def is_logged(self, agent_id):
        availability = self.innerdata.xod_status['agents'][str(agent_id)]['availability']
        return availability != AgentStatus.logged_out

    def set_on_call(self, agent_id, on_call):
        agent_status = self.innerdata.xod_status['agents'][str(agent_id)]
        agent_status['on_call'] = on_call

    def on_call(self, agent_id):
        agent_status = self.innerdata.xod_status['agents'][str(agent_id)]
        return agent_status['on_call']
