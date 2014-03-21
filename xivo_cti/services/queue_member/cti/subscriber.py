# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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
