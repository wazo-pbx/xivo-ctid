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

class StatisticsProducerInitializer(object):

    def __init__(self, queue_service_manager, queue_member_manager, agent_client):
        self.queue_service_manager = queue_service_manager
        self._queue_member_manager = queue_member_manager
        self.agent_client = agent_client

    def init_queue_statistics_producer(self, queue_statistics_producer):
        self._add_queues(queue_statistics_producer)
        self._add_queue_members(queue_statistics_producer)
        self._add_logged_agents(queue_statistics_producer)

    def _add_queues(self, queue_statistics_producer):
        queue_ids = self.queue_service_manager.get_queue_ids()
        for queue_id in queue_ids:
            queue_statistics_producer.on_queue_added(queue_id)

    def _add_queue_members(self, queue_statistics_producer):
        for queue_member in self._queue_member_manager.get_queue_members():
            queue_statistics_producer.on_queue_member_added(queue_member)

    def _add_logged_agents(self, queue_statistics_producer):
        for agent_status in self.agent_client.get_agent_statuses():
            if agent_status.logged:
                agent_id = 'Agent/%s' % agent_status.number
                queue_statistics_producer.on_agent_loggedon(agent_id)
