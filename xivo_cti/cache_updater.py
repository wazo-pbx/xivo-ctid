# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_bus.resources.user_line.event import UserLineAssociatedEvent
from xivo_cti.bus_listener import bus_listener_thread, ack_bus_message

logger = logging.getLogger(__name__)


class CacheUpdater(object):

    def __init__(self, bus_listener, task_queue, xivo_uuid):
        bus_listener.add_callback(UserLineAssociatedEvent.routing_key, self.on_bus_user_line_associated)
        self._task_queue = task_queue
        self._xivo_uuid = xivo_uuid

    def _on_user_line_associated(self, user_id, line_id):
        logger.debug('********************************************************************************')
        logger.debug('user %s has been associated to line %s', user_id, line_id)
        logger.debug('********************************************************************************')

    @bus_listener_thread
    @ack_bus_message
    def on_bus_user_line_associated(self, event):
        try:
            if event['origin_uuid'] != self._xivo_uuid:
                return

            user_id = event['data']['user_id']
            line_id = event['data']['line_id']
            self._task_queue.put(self._on_user_line_associated, user_id, line_id)
        except (KeyError, TypeError):
            logger.info('received a malformed UserLineAssociated event')
