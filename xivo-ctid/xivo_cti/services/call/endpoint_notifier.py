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


class EndpointNotifier(object):

    def __init__(self, pubsub):
        self._callbacks = {}
        self._pubsub = pubsub

    def notify(self, event):
        extension = event.extension
        self._pubsub.publish(('status', extension), event)

    def subscribe_to_status_changes(self, extension, callback):
        self._pubsub.subscribe(('status', extension), callback)

    def unsubscribe_from_status_changes(self, extension, callback):
        self._pubsub.unsubscribe(('status', extension), callback)
