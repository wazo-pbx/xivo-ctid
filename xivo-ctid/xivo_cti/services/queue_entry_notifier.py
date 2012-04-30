#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import defaultdict


class QueueEntryNotifier(object):

    _instance = None

    MSG_TEMPLATE = {'class': 'queueentryupdate',
                    'state': None}

    def __init__(self):
        self._subscriptions = defaultdict(set)
        self._cache = defaultdict(dict)

    def subscribe(self, client_connection, queue_name):
        self._subscriptions[queue_name].add(client_connection)
        if queue_name in self._cache:
            client_connection.send_message(self._cache[queue_name])

    def publish(self, queue_name, new_state):
        msg = dict(self.MSG_TEMPLATE)
        msg['state'] = new_state
        self._cache[queue_name] = msg
        for connection in self._subscriptions.get(queue_name, []):
            connection.send_message(msg)

    @classmethod
    def get_instance(cls):
        if cls._instance == None:
            cls._instance = cls()
        return cls._instance
