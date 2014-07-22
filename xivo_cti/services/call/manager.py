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


class CallManager(object):

    _answer_trigering_event = 'SIPRinging'

    def __init__(self, ami_class, ami_callback_handler):
        self._ami = ami_class
        self._ami_cb_handler = ami_callback_handler

    def hangup(self, call):
        logger.debug('Hanging up %s', call)
        self._ami.hangup(call.source._channel)

    def answer_next_ringing_call(self, connection, interface):
        fn = self._get_answer_on_sip_ringing_fn(connection, interface)
        self._ami_cb_handler.register_callback(self._answer_trigering_event, fn)

    def _get_answer_on_sip_ringing_fn(self, connection, interface):
        def answer_if_matching_peer(event):
            if event['Peer'].lower() != interface.lower():
                return

            self._ami_cb_handler.unregister_callback(self._answer_trigering_event,
                                                     answer_if_matching_peer)
            connection.answer_cb()

        return answer_if_matching_peer
