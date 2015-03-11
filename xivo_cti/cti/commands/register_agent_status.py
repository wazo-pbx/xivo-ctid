# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

from xivo_cti.cti.cti_command import CTICommandClass

logger = logging.getLogger(__name__)


def _parse(msg, command):
    command.agent_ids = [(xivo_uuid, agent_id) for (xivo_uuid, agent_id) in msg['agent_ids']]


RegisterAgentStatus = CTICommandClass('register_agent_status_update', None, _parse)
RegisterAgentStatus.add_to_registry()