# -*- coding: utf-8 -*-

# Copyright (C) 2007-2012  Avencall

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter


class AgentAvailabilityNotifier(object):

    def __init__(self, innerdata_dao, cti_server, cti_message_formatter=CTIMessageFormatter()):
        self.innerdata_dao = innerdata_dao
        self.cti_message_formatter = cti_message_formatter
        self.cti_server = cti_server

    def notify(self, agent_id):
        agent_status = self.innerdata_dao.agent_status(agent_id)
        cti_message = self.cti_message_formatter.update_agent_status(agent_id, agent_status)
        self.cti_server.send_cti_event(cti_message)
