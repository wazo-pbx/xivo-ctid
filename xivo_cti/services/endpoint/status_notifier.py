# -*- coding: utf-8 -*-
# Copyright 2014-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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
