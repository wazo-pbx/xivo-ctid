# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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
from xivo_dao import user_dao

logger = logging.getLogger(__name__)


class CurrentCallNotifier(object):

    def __init__(self, current_call_formatter):
        self._subscriptions = {}
        self._formatter = current_call_formatter

    def subscribe(self, client_connection):
        try:
            user_id = client_connection.user_id()
            line_identity = user_dao.get_line_identity(user_id).lower()
        except LookupError:
            logging.warning('User %s tried to subscribe to current_calls with no line' % user_id)
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
        formatted_current_call = self._formatter.get_line_current_call(line_identity)

        try:
            self._subscriptions[line_identity].send_message(formatted_current_call)
        except ClientConnection.CloseException:
            logger.info('Unsubscribing %s from current call updates' % line_identity)
            self._subscriptions.pop(line_identity, None)
