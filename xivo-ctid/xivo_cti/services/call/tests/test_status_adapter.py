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

import unittest

from mock import Mock, patch
from xivo_cti.services.agent.status_adapter import AgentStatusAdapter
from xivo_cti.services.agent.status_router import AgentStatusRouter
from xivo_cti.services.call.line_status import LineStatus
from xivo_cti.services.call.call_event import CallEvent


class TestStatusAdapter(unittest.TestCase):

    def setUp(self):
        self.router = Mock(AgentStatusRouter)
        self.adapter = AgentStatusAdapter(self.router)

    @patch('xivo_dao.agent_status_dao.get_agent_id_from_interface')
    def test_handle_call_event(self, get_agent_id_from_interface):
        agent_id = 1
        interface = 'SIP/abcd'
        status = LineStatus.talking

        event = Mock(CallEvent)
        event.endpoint_id = interface
        event.status = status

        get_agent_id_from_interface.return_value = agent_id

        self.adapter.handle_call_event(event)

        get_agent_id_from_interface.assert_called_once_with(interface)
        self.router.route.assert_called_once_with(agent_id, status)

    @patch('xivo_dao.agent_status_dao.get_agent_id_from_interface')
    def test_handle_call_event_with_no_agent(self, get_agent_id_from_interface):
        interface = 'SIP/abcd'
        status = LineStatus.talking

        get_agent_id_from_interface.side_effect = LookupError()

        event = Mock(CallEvent)
        event.endpoint_id = interface
        event.status = status

        self.adapter.handle_call_event(event)

        self.assertEquals(self.router.route.call_count, 0)

    #def test_listen_for_agent_events(self):
    #    agent_id = 1

    #    self.adapter.listen_for_agent_events(agent_id)

    #    notifier = Mock()
    #    notifier.subscribe_to_status_changes()


