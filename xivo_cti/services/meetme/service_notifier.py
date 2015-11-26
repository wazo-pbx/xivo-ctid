#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

from copy import deepcopy
from xivo_cti import config
from xivo_cti.services.meetme import encoder
from xivo_cti.client_connection import ClientConnection
from xivo_cti.database import user_db

from xivo_dao.helpers.db_utils import session_scope
from xivo_dao import user_line_dao

logger = logging.getLogger('meetme_service_notifier')


class MeetmeServiceNotifier(object):

    def __init__(self):
        self._subscriptions = {}
        self._current_state = None

    def subscribe(self, client_connection):
        try:
            user_id = client_connection.user_id()
            with session_scope():
                channel_pattern = user_line_dao.get_line_identity_by_user_id(user_id)
        except LookupError:
            logger.warning('Meetme subscription failed')
        else:
            self._subscriptions[client_connection] = {'channel_start': channel_pattern,
                                                      'membership': []}
            try:
                self._push_to_client(client_connection)
                self._send_meetme_membership()
            except ClientConnection.CloseException:
                self._subscriptions.pop(client_connection, None)

    def publish_meetme_update(self, meetme_status):
        if self._current_state == meetme_status:
            return
        self._current_state = deepcopy(meetme_status)
        self._send_room_configs()
        self._send_meetme_membership()

    def _send_meetme_membership(self):
        for connection, room_config in self._subscriptions.iteritems():
            chan_start = room_config['channel_start']
            pairs = self._get_room_number_for_chan_start(chan_start)
            membership = encoder.encode_room_number_pairs(pairs)
            if room_config['membership'] != membership:
                room_config['membership'] = deepcopy(membership)
                connection.send_message(membership)

    def _get_room_number_for_chan_start(self, chan_start):
        pairs = []

        for room, room_config in self._current_state.iteritems():
            for number, member in room_config['members'].iteritems():
                if chan_start.lower() in member['channel'].lower():
                    pairs.append((room, number))

        return pairs

    def _send_room_configs(self):
        to_remove = []
        for client_connection in self._subscriptions:
            try:
                self._push_to_client(client_connection)
            except ClientConnection.CloseException:
                to_remove.append(client_connection)
        for connection in to_remove:
            self._subscriptions.pop(connection, None)

    def _push_to_client(self, client_connection):
        if self._current_state:
            if bool(config['main']['context_separation']):
                user_id = client_connection.user_id()
                reachable_contexts = user_db.get_reachable_contexts(user_id)
                msg = encoder.encode_update_for_contexts(self._current_state, reachable_contexts)
            else:
                msg = encoder.encode_update(self._current_state)
            client_connection.send_message(msg)
