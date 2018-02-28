# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from collections import defaultdict

from xivo_dao.helpers.db_utils import session_scope
from xivo_dao import queue_dao


class QueueEntryNotifier(object):

    def __init__(self, cti_group_factory):
        self._cti_groups = defaultdict(cti_group_factory.new_cti_group)
        self._cache = {}

    def subscribe(self, client_connection, queue_id):
        with session_scope():
            queue_name = queue_dao.queue_name(queue_id)
        self._cti_groups[queue_name].add(client_connection)
        if queue_name in self._cache:
            client_connection.send_message(self._cache[queue_name])

    def publish(self, queue_name, new_state):
        self._cache[queue_name] = new_state

        cti_group = self._cti_groups.get(queue_name)
        if cti_group is not None:
            cti_group.send_message(new_state)
