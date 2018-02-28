# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging
from xivo_cti import dao
from xivo_cti.exception import NoSuchAgentException

logger = logging.getLogger(__name__)


class AgentAvailabilityUpdater(object):

    def __init__(self, agent_availability_notifier):
        self.notifier = agent_availability_notifier

    def update(self, agent_id, agent_status):
        try:
            dao.agent.set_agent_availability(agent_id, agent_status)
        except NoSuchAgentException:
            logger.info('Tried to update status of an unknown agent')
        else:
            self.notifier.notify(agent_id)
