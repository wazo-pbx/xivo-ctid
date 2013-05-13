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
from xivo_cti.exception import NoSuchAgentException

logger = logging.getLogger(__name__)


class AgentAvailabilityUpdater(object):

    def __init__(self, agent_availability_notifier):
        self.notifier = agent_availability_notifier

    def update(self, agent_id, agent_status):
        try:
            dao.innerdata.set_agent_availability(agent_id, agent_status)
        except NoSuchAgentException:
            logger.info('Tried to update status of an unknown agent')
        else:
            self.notifier.notify(agent_id)
