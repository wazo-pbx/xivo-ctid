# -*- coding: UTF-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
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
