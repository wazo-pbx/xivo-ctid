# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo_cti.model.endpoint_event import EndpointEvent
from xivo_cti.model.endpoint_status import EndpointStatus
from xivo_cti.model.call_event import CallEvent
from xivo_cti.model.call_status import CallStatus
from xivo_cti.services.call.call import Call


class CallStorage(object):

    def __init__(self, endpoint_notifier, call_notifier):
        self._endpoint_notifier = endpoint_notifier
        self._call_notifier = call_notifier
        self._endpoints = {}
        self._calls = {}

    def get_status_for_extension(self, extension):
        return self._endpoints.get(extension, EndpointStatus.available)

    def find_all_calls_for_extension(self, extension):
        result = [call for call in self._calls.itervalues()
                  if call.source.extension == extension or call.destination.extension == extension]
        return result

    def update_endpoint_status(self, extension, status):
        if self._need_to_update(extension, status):
            self._update(extension, status)
            self._notify_endpoint(extension, status)

    def new_call(self, uniqueid, destination_uniqueid, source, destination):
        self.end_call(uniqueid)
        self.end_call(destination_uniqueid)

        self._calls[uniqueid] = Call(source, destination)
        event = CallEvent(uniqueid=uniqueid,
                          source=source.extension,
                          destination=destination.extension,
                          status=CallStatus.ringing)
        self._call_notifier.notify(event)

    def end_call(self, uniqueid):
        if uniqueid not in self._calls:
            return

        source_channel = self._calls[uniqueid].source
        destination_channel = self._calls[uniqueid].destination
        event = CallEvent(uniqueid=uniqueid,
                          source=source_channel.extension,
                          destination=destination_channel.extension,
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

    def _notify_endpoint(self, extension, status):
        calls = self.find_all_calls_for_extension(extension)
        event = EndpointEvent(extension, status, calls)
        self._endpoint_notifier.notify(event)
