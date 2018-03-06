# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+


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
