# -*- coding: utf-8 -*-
# Copyright 2006-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_bus.resources.user_line.event import UserLineAssociatedEvent
from xivo_cti.bus_listener import bus_listener_thread, ack_bus_message

logger = logging.getLogger(__name__)


class CacheUpdater(object):

    def __init__(self, task_queue, xivo_uuid, innerdata):
        self._task_queue = task_queue
        self._xivo_uuid = xivo_uuid
        self._innerdata = innerdata

    def subscribe_to_bus(self, bus_listener):
        bus_listener.add_callback(UserLineAssociatedEvent.routing_key_fmt, self.on_bus_user_line_associated)

    def _on_user_line_associated(self, user_id, line_id):
        self._innerdata.update_config_list('users', 'edit', user_id)
        self._innerdata.update_config_list('phones', 'add', line_id)

    @bus_listener_thread
    @ack_bus_message
    def on_bus_user_line_associated(self, event):
        try:
            if event['origin_uuid'] != self._xivo_uuid:
                return

            user_id = str(event['data']['user_id'])
            line_id = str(event['data']['line_id'])
            self._task_queue.put(self._on_user_line_associated, user_id, line_id)
        except (KeyError, TypeError):
            logger.info('received a malformed UserLineAssociated event')
