# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_ctid_ng_client import Client as CtidNgClient

from xivo_cti import config, dao
from xivo_cti.bus_listener import bus_listener_thread, ack_bus_message
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter

logger = logging.getLogger(__name__)


class ChatPublisher(object):

    def __init__(self, bus_publisher, bus_listener, cti_server, task_queue, xivo_uuid):
        self._publisher = bus_publisher
        self._xivo_uuid = xivo_uuid
        self._cti_server = cti_server
        self._task_queue = task_queue

        chat_msg_routing_key = 'chat.message.{}.*.received'.format(self._xivo_uuid)
        bus_listener.add_callback(chat_msg_routing_key, self._on_bus_chat_message_event)

    def deliver_chat_message(self, from_, to, alias, text):
        destination_xivo_uuid, destination_user_uuid = to
        if destination_xivo_uuid != self._xivo_uuid:
            return

        destination_user_id = dao.user.get_by_uuid(destination_user_uuid)['id']
        destination = '{}/{}'.format(destination_xivo_uuid, destination_user_id)

        msg = CTIMessageFormatter.chat(from_, to, alias, text)
        self._cti_server.send_to_cti_client(destination, msg)

    def on_cti_chat_message(self, auth_token, local_user_uuid, remote_xivo_uuid, remote_user_uuid, alias, text):
        client = self._new_ctid_ng_client(auth_token)
        client.chats.send_message_from_user(remote_user_uuid, alias, text, to_xivo_uuid=remote_xivo_uuid)

    @bus_listener_thread
    @ack_bus_message
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

    @staticmethod
    def _new_ctid_ng_client(auth_token):
        return CtidNgClient(token=auth_token, **config['ctid_ng'])
