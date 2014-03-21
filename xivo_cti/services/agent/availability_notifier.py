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
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter
from xivo_cti import dao

logger = logging.getLogger(__name__)


class AgentAvailabilityNotifier(object):

    def __init__(self, cti_server):
        self.cti_server = cti_server

    def notify(self, agent_id):
        agent_status = dao.agent.agent_status(agent_id)
        cti_message = CTIMessageFormatter.update_agent_status(agent_id, agent_status)
        self.cti_server.send_cti_event(cti_message)
