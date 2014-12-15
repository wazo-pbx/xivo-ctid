# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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

from xivo_bus.resources.cti.event import EndpointStatusUpdateEvent
from xivo_cti import config
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter


class StatusNotifier(object):

    def __init__(self, cti_server, bus_producer):
        self._ctiserver = cti_server
        self._bus_producer = bus_producer

    def notify(self, phone_id, status):
        event = CTIMessageFormatter.phone_hintstatus_update(phone_id, status)
        self._ctiserver.send_cti_event(event)
        bus_event = EndpointStatusUpdateEvent(config['uuid'], phone_id, status)
        self._bus_status_notifier.publish_event(
            config['status_notifier']['exchange_name'],
            config['status_notifier']['routing_keys']['endpoint'],
            bus_event,
        )
