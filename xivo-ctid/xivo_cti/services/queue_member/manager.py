# -*- coding: UTF-8 -*-

import logging
from xivo_cti.services.queue_member import common

logger = logging.getLogger('QueueMemberManager')


class QueueMemberManager(object):

    def __init__(self, queue_member_notifier):
        self._queue_member_notifier = queue_member_notifier
        self._queue_members_by_id = {}

    def get_queue_member(self, queue_member_id):
        return self._queue_members_by_id.get(queue_member_id)

    def get_queue_member_by_name(self, queue_name, member_name):
        queue_member_id = common.format_queue_member_id(queue_name, member_name)
        return self._queue_members_by_id.get(queue_member_id)

    def get_queue_members_id(self):
        return self._queue_members_by_id.keys()

    def get_queue_members(self):
        return self._queue_members_by_id.values()

    def get_queue_members_by_agent_number(self, agent_number):
        member_name = common.format_member_name_of_agent(agent_number)
        return self.get_queue_members_by_member_name(member_name)

    def get_queue_members_by_member_name(self, member_name):
        return [queue_member for
                queue_member in self._queue_members_by_id.itervalues() if
                queue_member.member_name == member_name]

    def get_paused_count_by_member_name(self, member_name):
        paused_count = 0
        for queue_member in self.get_queue_members_by_member_name(member_name):
            if queue_member.state.paused:
                paused_count += 1
        return paused_count

    def get_queue_count_by_member_name(self, member_name):
        queue_count = len(self.get_queue_members_by_member_name(member_name))
        return queue_count

    # package private method
    def _add_queue_member(self, queue_member):
        if queue_member.id in self._queue_members_by_id:
            logger.warning('could not add queue member %r: already added',
                           queue_member.id)
        else:
            self._queue_members_by_id[queue_member.id] = queue_member
            self._queue_member_notifier._on_queue_member_added(queue_member)

    # package private method
    def _update_queue_member(self, queue_member, new_state):
        old_state = queue_member.state
        if old_state == new_state:
            logger.debug('not updating queue member %r: already up to date',
                         queue_member.id)
        else:
            queue_member.state = new_state
            self._queue_member_notifier._on_queue_member_updated(queue_member)

    # package private method
    def _remove_queue_member(self, queue_member):
        if queue_member.id not in self._queue_members_by_id:
            logger.warning('could not remove queue member %r: no such queue member',
                           queue_member.id)
        else:
            del self._queue_members_by_id[queue_member.id]
            self._queue_member_notifier._on_queue_member_removed(queue_member)

    # package private method
    def _remove_queue_member_by_id(self, queue_member_id):
        queue_member = self._queue_members_by_id.get(queue_member_id)
        if queue_member is None:
            logger.warning('could not remove queue member %r: no such queue member',
                           queue_member_id)
        else:
            del self._queue_members_by_id[queue_member.id]
            self._queue_member_notifier._on_queue_member_removed(queue_member)
