# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter


class QueueMemberCTISubscriber(object):

    def on_queue_member_added(self, queue_member):
        queue_member_ids = [queue_member.id]
        message = CTIMessageFormatter.add_queue_members(queue_member_ids)
        self.send_cti_event(message)

    def on_queue_member_updated(self, queue_member):
        message = CTIMessageFormatter.update_queue_member_config(queue_member)
        self.send_cti_event(message)

    def on_queue_member_removed(self, queue_member):
        queue_member_ids = [queue_member.id]
        message = CTIMessageFormatter.delete_queue_members(queue_member_ids)
        self.send_cti_event(message)

    def subscribe_to_queue_member(self, queue_member_notifier):
        queue_member_notifier.subscribe_to_queue_member_add(self.on_queue_member_added)
        queue_member_notifier.subscribe_to_queue_member_update(self.on_queue_member_updated)
        queue_member_notifier.subscribe_to_queue_member_remove(self.on_queue_member_removed)
