# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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


logger = logging.getLogger(__name__)

# see include/asterisk/pbx.h for more definitions
AST_EXTENSION_STATE_RINGING = 1 << 3


class CallManager(object):

    def __init__(self, ami_class, ami_callback_handler):
        self._ami = ami_class
        self._ami_cb_handler = ami_callback_handler

    def hangup(self, call):
        logger.debug('Hanging up %s', call)
        self._ami.hangup(call.source._channel)

    def answer_next_ringing_call(self, connection, interface):
        fn = self._get_answer_on_exten_status_fn(connection, interface)
        self._ami_cb_handler.register_callback('ExtensionStatus', fn)

    def _get_answer_on_exten_status_fn(self, connection, interface):
        def answer_if_ringing(event):
            if not int(event['Status']) & AST_EXTENSION_STATE_RINGING:
                return

            if event['Hint'].lower() != interface.lower():
                return

            self._ami_cb_handler.unregister_callback('ExtensionStatus', answer_if_ringing)
            connection.answer_cb()

        return answer_if_ringing
