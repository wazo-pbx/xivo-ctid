# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall'
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


class AgentServiceCTIParser(object):

    def __init__(self, agent_service_manager):
        self._agent_service_manager = agent_service_manager

    def queue_add(self, member, queue):
        agent_id = self._extract_agent_id_from_member(member)
        queue_id = self._extract_queue_id_from_queue(queue)

        self._agent_service_manager.add_agent_to_queue(agent_id, queue_id)

    def queue_remove(self, member, queue):
        agent_id = self._extract_agent_id_from_member(member)
        queue_id = self._extract_queue_id_from_queue(queue)

        self._agent_service_manager.remove_agent_from_queue(agent_id, queue_id)

    def queue_pause(self, member, queue):
        agent_id = self._extract_agent_id_from_member(member)
        queue_id = self._extract_queue_id_from_queue(queue)

        if queue_id == 'all':
            self._agent_service_manager.pause_agent_on_all_queues(agent_id)
        else:
            self._agent_service_manager.pause_agent_on_queue(agent_id, queue_id)

    def queue_unpause(self, member, queue):
        agent_id = self._extract_agent_id_from_member(member)
        queue_id = self._extract_queue_id_from_queue(queue)

        if queue_id == 'all':
            self._agent_service_manager.unpause_agent_on_all_queues(agent_id)
        else:
            self._agent_service_manager.unpause_agent_on_queue(agent_id, queue_id)

    def _extract_agent_id_from_member(self, member):
        agent_xid = member.split(':', 1)[1]
        agent_id = agent_xid.split('/', 1)[1]
        return int(agent_id)

    def _extract_queue_id_from_queue(self, queue):
        queue_xid = queue.split(':', 1)[1]
        queue_id = queue_xid.split('/', 1)[1]
        if queue_id == 'all':
            return queue_id
        else:
            return int(queue_id)
