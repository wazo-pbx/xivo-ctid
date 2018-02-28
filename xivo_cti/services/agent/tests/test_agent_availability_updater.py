# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, patch
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.services.agent.availability_updater import AgentAvailabilityUpdater
from xivo_cti.services.agent.availability_notifier import AgentAvailabilityNotifier
from xivo_cti.exception import NoSuchAgentException


class TestAgentAvailabilityUpdater(unittest.TestCase):

    def setUp(self):
        self.notifier = Mock(AgentAvailabilityNotifier)
        self.agent_availability_updater = AgentAvailabilityUpdater(self.notifier)

    @patch('xivo_cti.dao.agent')
    def test_update(self, agent_dao):
        agent_id = 13
        agent_status = AgentStatus.available

        self.agent_availability_updater.update(agent_id, agent_status)

        agent_dao.set_agent_availability.assert_called_once_with(agent_id, agent_status)
        self.agent_availability_updater.notifier.notify.assert_called_once_with(agent_id)

    @patch('xivo_cti.dao.agent')
    def test_update_no_such_agent(self, agent_dao):
        agent_id = 13
        agent_status = AgentStatus.available
        agent_dao.set_agent_availability.side_effect = NoSuchAgentException()

        self.agent_availability_updater.update(agent_id, agent_status)

        self.assertEquals(self.notifier.notify.call_count, 0)
