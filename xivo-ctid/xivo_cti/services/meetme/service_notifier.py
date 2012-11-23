#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2012 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from copy import deepcopy
from xivo_cti.services.meetme import encoder
from xivo_cti.client_connection import ClientConnection
from xivo_cti.cti_config import Config
from xivo_cti.dao import userfeaturesdao

logger = logging.getLogger('meetme_service_notifier')


class MeetmeServiceNotifier(object):

    def __init__(self):
        self._subscriptions = {}
        self._current_state = None

    def subscribe(self, client_connection):
        try:
            user_id = client_connection.user_id()
            reachable_contexts = self.user_features_dao.get_reachable_contexts(user_id)
            channel_pattern = userfeaturesdao.get_line_identity(user_id)
        except LookupError:
            logger.warning('Meetme subscription failed')
        else:
            self._subscriptions[client_connection] = {'client_connection': client_connection,
                                                      'contexts': reachable_contexts,
                                                      'channel_start': channel_pattern,
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
        for connection, config in self._subscriptions.iteritems():
            chan_start = config['channel_start']
            pairs = self._get_room_number_for_chan_start(chan_start)
            membership = encoder.encode_room_number_pairs(pairs)
            if self._subscriptions[connection]['membership'] != membership:
                self._subscriptions[connection]['membership'] = deepcopy(membership)
                connection.send_message(membership)

    def _get_room_number_for_chan_start(self, chan_start):
        pairs = []

        for room, config in self._current_state.iteritems():
            for number, member in config['members'].iteritems():
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
            if Config.get_instance().part_context():
                user_id = client_connection.user_id()
                reachable_contexts = self.user_features_dao.get_reachable_contexts(user_id)
                msg = encoder.encode_update_for_contexts(self._current_state, reachable_contexts)
            else:
                msg = encoder.encode_update(self._current_state)
            client_connection.send_message(msg)
