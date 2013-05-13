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

from xivo_cti import dao
from xivo_cti.services.current_call.manager import PEER_CHANNEL
from xivo_cti.services.current_call.manager import BRIDGE_TIME
from xivo_cti.services.current_call.manager import ON_HOLD

logger = logging.getLogger(__name__)


class CurrentCallFormatter(object):

    def __init__(self):
        self._current_call_manager = None

    def get_line_current_call(self, line_identity):
        calls = []

        current_calls = self._current_call_manager.get_line_calls(line_identity)
        for call in current_calls:
            try:
                formatted_call = self._format_call(call)
            except LookupError:
                logger.warning('Could not retrieve channel information for the following call %s', call)
            else:
                calls.append(formatted_call)

        return {'class': 'current_calls',
                'current_calls': calls}

    def _format_call(self, call):
        caller_id = dao.channel.get_caller_id_name_number(call[PEER_CHANNEL])
        if call[ON_HOLD] is False:
            status = 'up'
        else:
            status = 'hold'
        return {'cid_name': caller_id[0],
                'cid_number': caller_id[1],
                'call_status': status,
                'call_start': call[BRIDGE_TIME]}

    def attended_transfer_answered(self, line_identity):
        return {'class': 'current_call_attended_transfer_answered',
                'line': line_identity}
