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

from collections import defaultdict
from xivo_dao import queue_dao


class QueueEntryNotifier(object):

    def __init__(self, cti_group_factory):
        self._cti_groups = defaultdict(cti_group_factory.new_cti_group)
        self._cache = {}

    def subscribe(self, client_connection, queue_id):
        queue_name = queue_dao.queue_name(queue_id)
        self._cti_groups[queue_name].add(client_connection)
        if queue_name in self._cache:
            client_connection.send_message(self._cache[queue_name])

    def publish(self, queue_name, new_state):
        self._cache[queue_name] = new_state

        cti_group = self._cti_groups.get(queue_name)
        if cti_group is not None:
            cti_group.send_message(new_state)
