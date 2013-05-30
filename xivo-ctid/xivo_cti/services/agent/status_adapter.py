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

from xivo_dao import agent_status_dao


logger = logging.getLogger(__name__)


class AgentStatusAdapter(object):

    def __init__(self, status_router):
        self._status_router = status_router

    def handle_call_event(self, call_event):
        try:
            agent_id = agent_status_dao.get_agent_id_from_interface(call_event.endpoint_id)
        except LookupError:
            logger.debug('endpoint %s has no agent', call_event.endpoint_id)
        else:
            self._status_router.route(agent_id, call_event.status)
