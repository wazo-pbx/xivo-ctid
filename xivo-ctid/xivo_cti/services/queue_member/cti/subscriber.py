# -*- coding: UTF-8 -*-


class QueueMemberCTISubscriber(object):

    def __init__(self, cti_message_formatter):
        self._cti_message_formatter = cti_message_formatter

    def on_queue_member_added(self, queue_member):
        queue_member_ids = [queue_member.id]
        message = self._cti_message_formatter.add_queue_members(queue_member_ids)
        self.send_cti_event(message)

    def on_queue_member_updated(self, queue_member):
        message = self._cti_message_formatter.update_queue_member_config(queue_member)
        self.send_cti_event(message)

    def on_queue_member_removed(self, queue_member):
        queue_member_ids = [queue_member.id]
        message = self._cti_message_formatter.delete_queue_members(queue_member_ids)
        self.send_cti_event(message)

    def subscribe_to_queue_member(self, queue_member_notifier):
        queue_member_notifier.subscribe_to_queue_member_add(self.on_queue_member_added)
        queue_member_notifier.subscribe_to_queue_member_update(self.on_queue_member_updated)
        queue_member_notifier.subscribe_to_queue_member_remove(self.on_queue_member_removed)
