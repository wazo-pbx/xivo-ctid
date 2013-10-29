# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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


class QueueMemberNotifier(object):

    def __init__(self):
        self._callbacks_on_add = []
        self._callbacks_on_update = []
        self._callbacks_on_remove = []

    def subscribe_to_queue_member_add(self, callback):
        self._callbacks_on_add.append(callback)

    def subscribe_to_queue_member_update(self, callback):
        self._callbacks_on_update.append(callback)

    def subscribe_to_queue_member_remove(self, callback):
        self._callbacks_on_remove.append(callback)

    # package private method
    def _on_queue_member_added(self, queue_member):
        self._call_callbacks(self._callbacks_on_add, queue_member)

    # package private method
    def _on_queue_member_updated(self, queue_member):
        self._call_callbacks(self._callbacks_on_update, queue_member)

    # package private method
    def _on_queue_member_removed(self, queue_member):
        self._call_callbacks(self._callbacks_on_remove, queue_member)

    def _call_callbacks(self, callbacks, queue_member):
        for callback in callbacks:
            callback(queue_member)
