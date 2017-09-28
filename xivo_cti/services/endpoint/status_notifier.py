# -*- coding: utf-8 -*-

# Copyright 2014-2017 The Wazo Authors  (see the AUTHORS file)
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
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter


class StatusNotifier(object):

    def __init__(self, cti_server, bus_publisher, innerdata):
        self._ctiserver = cti_server
        self._bus_publisher = bus_publisher
        self._innerdata = innerdata

    def notify(self, phone_id, status):
        cti_event = CTIMessageFormatter.phone_hintstatus_update(phone_id, status)
        self._ctiserver.send_cti_event(cti_event)
        bus_event = EndpointStatusUpdateEvent(phone_id, status)
        user_id = self._innerdata.xod_config['phones'].keeplist[phone_id]['iduserfeatures']
        user_uuid = self._innerdata.xod_config['users'].keeplist[str(user_id)]['uuid']
        headers = {'user_uuid:{uuid}'.format(uuid=user_uuid): True}
        self._bus_publisher.publish(bus_event, headers=headers)
