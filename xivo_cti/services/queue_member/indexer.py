# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti import dao


class QueueMemberIndexer(object):

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
