# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

import logging

from xivo_cti.client_connection import ClientConnection

logger = logging.getLogger(__name__)


class CTIGroup(object):

    def __init__(self, cti_msg_encoder):
        self._cti_msg_encoder = cti_msg_encoder
        self._interfaces = set()

    def add(self, interface_cti):
        if interface_cti.state() == interface_cti.STATE_DISCONNECTED:
            return

        interface_cti.attach_observer(self._on_interface_cti_update)
        self._interfaces.add(interface_cti)

    def remove(self, interface_cti):
        self._interfaces.discard(interface_cti)
        interface_cti.detach_observer(self._on_interface_cti_update)

    def _on_interface_cti_update(self, interface_cti, state):
        if state == interface_cti.STATE_DISCONNECTED:
            self._interfaces.discard(interface_cti)

    def send_message(self, msg):
        data = self._cti_msg_encoder.encode(msg)
        closed_interfaces = []
        for interface in self._interfaces:
            try:
                interface.send_encoded_message(data)
            except ClientConnection.CloseException:
                logger.warning('Error while calling send_encoded_message: connection closed', exc_info=True)
                closed_interfaces.append(interface)

        for closed_interface in closed_interfaces:
            self._interfaces.remove(closed_interface)


class CTIGroupFactory(object):

    def __init__(self, cti_msg_encoder):
        self._cti_msg_encoder = cti_msg_encoder

    def new_cti_group(self):
        return CTIGroup(self._cti_msg_encoder)
