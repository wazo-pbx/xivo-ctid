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

from mock import Mock
from xivo.asterisk.extension import Extension
from xivo_cti.services.agent.status_manager import AgentStatusManager
from xivo_cti.services.agent.status_router import AgentStatusRouter
from xivo_cti.services.call.direction import CallDirection
from xivo_cti.services.call.storage import Call
from xivo_cti.model.endpoint_event import EndpointEvent
from xivo_cti.model.endpoint_status import EndpointStatus


class TestStatusRouter(unittest.TestCase):

    def setUp(self):
        self.status_manager = Mock(AgentStatusManager)
        self.router = AgentStatusRouter(self.status_manager)

    def test_route_device_not_in_use(self):
        agent_id = 1
        extension = Extension('9327', 'a_context')
        status = EndpointStatus.available
        calls = []
        event = EndpointEvent(extension, status, calls)

        self.router.route(agent_id, event)

        self.status_manager.device_not_in_use.assert_called_once_with(agent_id)

    def test_route_device_in_use_no_calls(self):
        agent_id = 1
        extension = Extension('9327', 'a_context')
        status = EndpointStatus.talking
        calls = []
        event = EndpointEvent(extension, status, calls)
        expected_direction = CallDirection.outgoing
        expected_is_internal = True

        self.router.route(agent_id, event)

        self.status_manager.device_in_use.assert_called_once_with(agent_id, expected_direction, expected_is_internal)

    def test_route_device_in_use_incoming_internal(self):
        agent_id = 1
        is_internal = True
        expected_direction = CallDirection.incoming
        expected_is_internal = is_internal
        extension = Extension('9327', 'a_context')
        status = EndpointStatus.talking
        calls = [Call(source=Mock(Call), destination=extension, is_internal=is_internal)]
        event = EndpointEvent(extension, status, calls)

        self.router.route(agent_id, event)

        self.status_manager.device_in_use.assert_called_once_with(agent_id, expected_direction, expected_is_internal)

    def test_route_device_in_use_outgoing_external(self):
        agent_id = 1
        is_internal = False
        expected_is_internal = is_internal
        expected_direction = CallDirection.outgoing
        extension = Extension('9327', 'a_context')
        status = EndpointStatus.talking
        calls = [Call(source=extension, destination=Mock(Extension), is_internal=is_internal)]
        event = EndpointEvent(extension, status, calls)

        self.router.route(agent_id, event)

        self.status_manager.device_in_use.assert_called_once_with(agent_id, expected_direction, expected_is_internal)
