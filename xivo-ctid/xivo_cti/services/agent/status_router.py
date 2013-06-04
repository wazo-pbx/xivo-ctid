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
# along with this program.  If not, see <http://www.gnu.org/license

from xivo_cti.model.endpoint_status import EndpointStatus


class AgentStatusRouter(object):

    def __init__(self, agent_status_manager):
        self._status_manager = agent_status_manager

    def route(self, agent_id, status):
        if status == EndpointStatus.available:
            self._status_manager.device_not_in_use(agent_id)
        elif status == EndpointStatus.talking:
            self._status_manager.device_in_use(agent_id)
