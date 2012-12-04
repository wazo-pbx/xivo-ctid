# -*- coding: utf-8 -*-

import logging

from xivo_cti.dao import userfeaturesdao
from xivo_cti.client_connection import ClientConnection

logger = logging.getLogger(__name__)


class CurrentCallNotifier(object):

    def __init__(self, formatter):
        self._subscriptions = {}
        self._formatter = formatter

    def subscribe(self, client_connection):
        try:
            user_id = client_connection.user_id()
            line_identity = userfeaturesdao.get_line_identity(user_id)
        except LookupError:
            logging.warning('User %s tried to subscribe to current_calls with no line' % user_id)
        else:
            self._subscriptions[line_identity] = client_connection
            self._report_current_call(line_identity)

    def publish_current_call(self, line_identity):
        if line_identity in self._subscriptions:
            self._report_current_call(line_identity)

    def _report_current_call(self, line_identity):
        formatted_current_call = self._formatter.get_line_current_call(line_identity)

        try:
            self._subscriptions[line_identity].send_message(formatted_current_call)
        except ClientConnection.CloseException:
            logger.info('Unsubscribing %s from current call updates' % line_identity)
            self._subscriptions.pop(line_identity, None)
