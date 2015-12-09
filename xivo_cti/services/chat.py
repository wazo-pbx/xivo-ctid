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

import logging

from xivo_bus.resources.chat.event import ChatMessageEvent
from xivo_cti.bus_listener import bus_listener_thread, loads_and_ack
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter

logger = logging.getLogger(__name__)


class ChatPublisher(object):

    def __init__(self, bus_publisher, bus_listener, cti_server, task_queue, xivo_uuid):
        self._publisher = bus_publisher
        self._xivo_uuid = xivo_uuid
        self._cti_server = cti_server
        self._task_queue = task_queue

        chat_msg_routing_key = 'chat.message.{}.#'.format(self._xivo_uuid)
        bus_listener.add_callback(chat_msg_routing_key, self._on_bus_chat_message_event)

    def deliver_chat_message(self, from_, to, alias, text):
        destination = '{}/{}'.format(*to)
        msg = CTIMessageFormatter.chat(from_, to, alias, text)
        self._cti_server.send_to_cti_client(destination, msg)

    def on_cti_chat_message(self, local_user_id, remote_xivo_uuid, remote_user_id, alias, text):
        from_ = self._xivo_uuid, local_user_id
        to = remote_xivo_uuid, remote_user_id
        self._send_chat_msg_to_bus(from_, to, alias, text)

    def _send_chat_msg_to_bus(self, from_, to, alias, text):
        bus_msg = ChatMessageEvent(from_, to, alias, text)
        self._publisher.publish(bus_msg)

    @bus_listener_thread
    @loads_and_ack
    def _on_bus_chat_message_event(self, event):
        data = event.get('data', {})
        try:
            from_ = data['from']
            to = data['to']
            alias = data['alias']
            text = data['msg']

            self._task_queue.put(self.deliver_chat_message, from_, to, alias, text)
        except KeyError as e:
            logger.info('_on_bus_chat_message_event: received an incomplete chat message event: %s', e)
