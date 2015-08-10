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

from xivo_cti.client_connection import ClientConnection
from xivo_dao import user_line_dao

logger = logging.getLogger(__name__)


class CurrentCallNotifier(object):

    def __init__(self, current_call_formatter):
        self._subscriptions = {}
        self._formatter = current_call_formatter

    def subscribe(self, client_connection):
        try:
            user_id = client_connection.user_id()
            line_identity = user_line_dao.get_line_identity_by_user_id(user_id).lower()
        except LookupError:
            logging.warning('User %s tried to subscribe to current_calls with no line', user_id)
        else:
            self._subscriptions[line_identity] = client_connection
            logger.info('User %s is now registered to current_calls on line %s', user_id, line_identity)
            self._report_current_call(line_identity)

    def publish_current_call(self, line_identity):
        line_identity = line_identity.lower()
        if line_identity in self._subscriptions:
            self._report_current_call(line_identity)

    def _report_current_call(self, line_identity):
        line_identity = line_identity.lower()
        formatted_message = self._formatter.get_line_current_call(line_identity)
        self._send_message(line_identity, formatted_message)

    def attended_transfer_answered(self, line_identity):
        line_identity = line_identity.lower()
        formatted_message = self._formatter.attended_transfer_answered(line_identity)
        self._send_message(line_identity, formatted_message)

    def _send_message(self, line_identity, message):
        client_connection = self._subscriptions.get(line_identity)
        if client_connection is None:
            return

        try:
            client_connection.send_message(message)
        except ClientConnection.CloseException:
            logger.info('Unsubscribing %s from current call updates' % line_identity)
            del self._subscriptions[line_identity]
