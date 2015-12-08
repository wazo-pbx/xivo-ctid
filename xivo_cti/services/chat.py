# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

from xivo_bus.resources.chat.event import ChatMessageEvent


class ChatPublisher(object):

    def __init__(self, bus_publisher, xivo_uuid):
        self._publisher = bus_publisher
        self._xivo_uuid = xivo_uuid

    def on_chat_message(self, local_user_id, remote_xivo_uuid, remote_user_id, alias, text):
        from_ = self._xivo_uuid, local_user_id
        to = remote_xivo_uuid, remote_user_id

        bus_msg = ChatMessageEvent(from_, to, alias, text)
        self._publisher.publish(bus_msg)
