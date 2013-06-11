# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from collections import namedtuple
from xivo_cti.model.endpoint_event import EndpointEvent
from xivo_cti.model.endpoint_status import EndpointStatus
from xivo_cti.model.call_event import CallEvent
from xivo_cti.model.call_status import CallStatus

Call = namedtuple('Call', ['source', 'destination'])


class CallStorage(object):

    def __init__(self, endpoint_notifier, call_notifier):
        self._endpoint_notifier = endpoint_notifier
        self._call_notifier = call_notifier
        self._endpoints = {}
        self._calls = {}

    def get_status_for_extension(self, extension):
        return self._endpoints.get(extension, EndpointStatus.available)

    def update_endpoint_status(self, extension, status):
        if self._need_to_update(extension, status):
            self._update(extension, status)
            self._notify(extension, status)

    def new_call(self, uniqueid, source, destination):
        if uniqueid not in self._calls:
            self._calls[uniqueid] = Call(source, destination)
            event = CallEvent(uniqueid=uniqueid,
                              source=source,
                              destination=destination,
                              status=CallStatus.ringing)
            self._call_notifier.notify(event)

    def end_call(self, uniqueid):
        if uniqueid in self._calls:
            source = self._calls[uniqueid].source
            destination = self._calls[uniqueid].destination
            event = CallEvent(uniqueid=uniqueid,
                              source=source,
                              destination=destination,
                              status=CallStatus.hangup)
            self._call_notifier.notify(event)
            self._calls.pop(uniqueid)

    def _need_to_update(self, extension, status):
        return extension not in self._endpoints or self._endpoints[extension] != status

    def _update(self, extension, status):
        if status == EndpointStatus.available:
            self._endpoints.pop(extension, None)
        else:
            self._endpoints[extension] = status

    def _notify(self, extension, status):
        event = EndpointEvent(extension, status)
        self._endpoint_notifier.notify(event)
