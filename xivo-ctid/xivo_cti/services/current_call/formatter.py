# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
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

from xivo_cti import dao

logger = logging.getLogger(__name__)


class CurrentCallFormatter(object):

    def __init__(self):
        self._state = {}

    def get_line_current_call(self, line_identity):
        calls = []

        for call in self._state.get(line_identity, {}):
            try:
                formatted_call = self._format_call(call)
            except LookupError:
                logger.warning('Could not retrieve channel information for the following call %s', call)
            else:
                calls.append(formatted_call)

        return {'class': 'current_calls',
                'current_calls': calls}

    def _format_call(self, call):
        caller_id = dao.channel.get_caller_id_name_number(call['channel'])
        return {'cid_name': caller_id[0],
                'cid_number': caller_id[1],
                'call_status': 'up',
                'call_start': call['bridge_time']}
