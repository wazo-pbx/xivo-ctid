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


class QueueMemberCTIAdapter(object):

    def __init__(self, queue_member_manager):
        self._queue_member_manager = queue_member_manager

    def get_list(self):
        return self._queue_member_manager.get_queue_members_id()

    def get_config(self, queue_member_id):
        queue_member = self._queue_member_manager.get_queue_member(queue_member_id)
        if queue_member is None:
            return {}
        else:
            return queue_member.to_cti_config()

    def get_status(self, queue_member_id):
        queue_member = self._queue_member_manager.get_queue_member(queue_member_id)
        if queue_member is None:
            return None
        else:
            return queue_member.to_cti_status()
