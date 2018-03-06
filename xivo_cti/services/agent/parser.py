# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+


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
