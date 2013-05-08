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
from xivo_cti import dao

logger = logging.getLogger('QueueMemberIndexer')


class QueueMemberIndexer(object):

    def __init__(self):
        pass

    def on_queue_member_added(self, queue_member):
        if queue_member.is_agent():
            queue_id = dao.queue.get_id_from_name(queue_member.queue_name)
            agent_interface = queue_member.member_name
            agent_id = dao.agent.get_id_from_interface(agent_interface)
            dao.agent.add_to_queue(agent_id, queue_id)

    def on_queue_member_removed(self, queue_member):
        if queue_member.is_agent():
            queue_id = dao.queue.get_id_from_name(queue_member.queue_name)
            agent_interface = queue_member.member_name
            agent_id = dao.agent.get_id_from_interface(agent_interface)
            dao.agent.remove_from_queue(agent_id, queue_id)

    def subscribe_to_queue_member(self, queue_member_notifier):
        queue_member_notifier.subscribe_to_queue_member_add(self.on_queue_member_added)
        queue_member_notifier.subscribe_to_queue_member_remove(self.on_queue_member_removed)

    def initialize(self, queue_member_manager):
        for queue_member in queue_member_manager.get_queue_members():
            self.on_queue_member_added(queue_member)
