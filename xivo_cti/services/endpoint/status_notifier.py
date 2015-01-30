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

from kombu import Connection
from kombu import Producer

from xivo_bus import Marshaler
from xivo_bus.resources.cti.event import EndpointStatusUpdateEvent
from xivo_cti import config
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter


class StatusNotifier(object):

    _marshaler = Marshaler()

    def __init__(self, cti_server, bus_exchange):
        self._ctiserver = cti_server
        self._exchange = bus_exchange

    def notify(self, phone_id, status):
        event = CTIMessageFormatter.phone_hintstatus_update(phone_id, status)
        self._ctiserver.send_cti_event(event)
        msg = self._marshaler.marshal_message(
            EndpointStatusUpdateEvent(config['uuid'], phone_id, status))
        bus_url = 'amqp://{username}:{password}@{host}:{port}//'.format(**config['bus'])
        with Connection(bus_url) as conn:
            producer = Producer(conn, exchange=self._exchange, auto_declare=True)
            producer.publish(msg, routing_key=config['bus']['routing_keys']['endpoint_status'])
