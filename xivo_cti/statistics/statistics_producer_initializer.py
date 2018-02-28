# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti import dao


class StatisticsProducerInitializer(object):

    def __init__(self, queue_member_manager, agentd_client):
        self._queue_member_manager = queue_member_manager
        self.agentd_client = agentd_client

    def init_queue_statistics_producer(self, queue_statistics_producer):
        self._add_queues(queue_statistics_producer)
        self._add_queue_members(queue_statistics_producer)
        self._add_logged_agents(queue_statistics_producer)

    def _add_queues(self, queue_statistics_producer):
        queue_ids = dao.queue.get_ids()
        for queue_id in queue_ids:
            queue_statistics_producer.on_queue_added(queue_id)

    def _add_queue_members(self, queue_statistics_producer):
        for queue_member in self._queue_member_manager.get_queue_members():
            queue_statistics_producer.on_queue_member_added(queue_member)

    def _add_logged_agents(self, queue_statistics_producer):
        for agent_status in self.agentd_client.agents.get_agent_statuses():
            if agent_status.logged:
                agent_id = 'Agent/%s' % agent_status.number
                queue_statistics_producer.on_agent_loggedon(agent_id)
