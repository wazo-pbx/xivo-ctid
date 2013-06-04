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

from xivo_dao import line_dao
from xivo_cti.services.call import helper
from xivo_cti.model.line_status import LineStatus


class CallReceiver(object):

    def __init__(self, call_storage, call_notifier):
        self._call_storage = call_storage
        self._call_notifier = call_notifier

    def handle_newstate(self, event):
        interface = self._interface_from_event(event)
        status = helper.channel_state_to_status(event['ChannelState'])

        self._update_interface_status(interface, status)

    def handle_hangup(self, event):
        interface = self._interface_from_event(event)
        status = LineStatus.available

        self._update_interface_status(interface, status)

    def _interface_from_event(self, event):
        channel = event['Channel']
        interface = helper.interface_from_channel(channel)
        return interface

    def _update_interface_status(self, interface, status):
        extension = line_dao.get_extension_from_interface(interface)
        self._call_storage.update_line_status(extension, status)
