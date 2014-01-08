# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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


class CallNotifier(object):
    def __init__(self, pubsub):
        self._pubsub = pubsub

    def notify(self, event):
        self._pubsub.publish(('calls_outgoing', event.source), event)
        self._pubsub.publish(('calls_incoming', event.destination), event)

    def subscribe_to_incoming_call_events(self, extension, callback):
        self._pubsub.subscribe(('calls_incoming', extension), callback)

    def subscribe_to_outgoing_call_events(self, extension, callback):
        self._pubsub.subscribe(('calls_outgoing', extension), callback)

    def unsubscribe_from_incoming_call_events(self, extension, callback):
        self._pubsub.unsubscribe(('calls_incoming', extension), callback)

    def unsubscribe_from_outgoing_call_events(self, extension, callback):
        self._pubsub.unsubscribe(('calls_outgoing', extension), callback)
