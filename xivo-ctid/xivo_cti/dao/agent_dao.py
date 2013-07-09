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
import time
from collections import namedtuple
from functools import wraps

from xivo_cti.exception import NoSuchAgentException

logger = logging.getLogger(__name__)


def notify_clients(decorated_func):
    @wraps(decorated_func)
    def wrapper(self, agent_id, *args, **kwargs):
        self.innerdata.handle_cti_stack('setforce', ('agents', 'updatestatus', str(agent_id)))
        decorated_func(self, agent_id, *args, **kwargs)
        try:
            self.innerdata.handle_cti_stack('empty_stack')
        except AttributeError:
            logger.debug("handle_cti_stack called before xivo-ctid is fully booted")
    return wrapper


AgentCallStatus = namedtuple('AgentCallStatus', ['is_acd', 'direction', 'is_internal'])


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

    def agent_status(self, agent_id):
        agent_status = self.innerdata.xod_status['agents'][str(agent_id)]
        return agent_status

    def set_agent_availability(self, agent_id, availability):
        agent_id = str(agent_id)
        if agent_id not in self.innerdata.xod_status['agents']:
            raise NoSuchAgentException('Unknown agent %s' % agent_id)
        agent_status = self.innerdata.xod_status['agents'][agent_id]
        if availability != agent_status['availability']:
            agent_status['availability_since'] = time.time()
            agent_status['availability'] = availability

    def is_completely_paused(self, agent_id):
        agent_interface = self.get_interface_from_id(agent_id)

        agent_membership_count = self._queue_member_manager.get_queue_count_by_member_name(agent_interface)
        if agent_membership_count == 0:
            return False

        paused_count = self._queue_member_manager.get_paused_count_by_member_name(agent_interface)
        return paused_count == agent_membership_count

    def set_on_call_acd(self, agent_id, on_call_acd):
        agent_status = self.innerdata.xod_status['agents'][str(agent_id)]
        agent_status['on_call_acd'] = on_call_acd

    def on_call_acd(self, agent_id):
        agent_status = self.innerdata.xod_status['agents'][str(agent_id)]
        return agent_status['on_call_acd']

    def set_on_wrapup(self, agent_id, on_wrapup):
        agent_status = self.innerdata.xod_status['agents'][str(agent_id)]
        agent_status['on_wrapup'] = on_wrapup

    def on_wrapup(self, agent_id):
        agent_status = self.innerdata.xod_status['agents'][str(agent_id)]
        return agent_status['on_wrapup']

    def set_call_status(self, agent_id, call_status):
        agent_status = self.innerdata.xod_status['agents'][str(agent_id)]
        agent_status['call_status'] = call_status

    def call_status(self, agent_id):
        agent_status = self.innerdata.xod_status['agents'][str(agent_id)]
        return agent_status['call_status']

    def call_direction(self, agent_id):
        agent_status = self.innerdata.xod_status['agents'][str(agent_id)]
        return agent_status['call_direction']

    @notify_clients
    def add_to_queue(self, agent_id, queue_id):
        queues = self.innerdata.xod_status['agents'][str(agent_id)]['queues']
        if(queues.count(str(queue_id)) == 0):
            queues.append(str(queue_id))

    @notify_clients
    def remove_from_queue(self, agent_id, queue_id):
        str_queue_id = str(queue_id)
        queues_before = self.innerdata.xod_status['agents'][str(agent_id)]['queues']
        queues_after = filter(lambda q: q != str_queue_id, queues_before)
        self.innerdata.xod_status['agents'][str(agent_id)]['queues'] = queues_after
