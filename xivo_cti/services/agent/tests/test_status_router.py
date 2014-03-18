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

import unittest

from mock import Mock
from xivo_cti.services.agent.status_manager import AgentStatusManager
from xivo_cti.services.agent.status_router import AgentStatusRouter
from xivo_cti.services.call.direction import CallDirection
from xivo_cti.services.call.storage import Call
from xivo_cti.model.endpoint_event import EndpointEvent
from xivo_cti.model.endpoint_status import EndpointStatus


AGENT_ID = 13
NUMBER = '5327'
CONTEXT = 'my_context'
EXTENSION = Mock(number=NUMBER, context=CONTEXT)


class TestStatusRouter(unittest.TestCase):

    def setUp(self):
        self.status_manager = Mock(AgentStatusManager)
        self.router = AgentStatusRouter(self.status_manager)

    def test_route_device_not_in_use(self):
        status = EndpointStatus.available
        calls = []
        event = EndpointEvent(EXTENSION, status, calls)

        self.router.route(AGENT_ID, event)

        self.status_manager.device_not_in_use.assert_called_once_with(AGENT_ID)

    def test_route_device_in_use_no_calls(self):
        status = EndpointStatus.talking
        calls = []
        event = EndpointEvent(EXTENSION, status, calls)
        expected_direction = CallDirection.outgoing
        expected_is_internal = True

        self.router.route(AGENT_ID, event)

        self.status_manager.device_in_use.assert_called_once_with(AGENT_ID, expected_direction, expected_is_internal)

    def test_route_device_in_use_incoming_internal(self):
        is_internal = True
        extension = Mock(number=NUMBER, context=CONTEXT, is_internal=is_internal)
        expected_direction = CallDirection.incoming
        expected_is_internal = is_internal
        status = EndpointStatus.talking
        calls = [Call(source=Mock(Call), destination=extension)]
        event = EndpointEvent(extension, status, calls)

        self.router.route(AGENT_ID, event)

        self.status_manager.device_in_use.assert_called_once_with(AGENT_ID, expected_direction, expected_is_internal)

    def test_route_device_in_use_outgoing_external(self):
        is_internal = False
        extension = Mock(number=NUMBER, context=CONTEXT, is_internal=is_internal)
        expected_is_internal = is_internal
        expected_direction = CallDirection.outgoing
        status = EndpointStatus.talking
        calls = [Call(source=extension, destination=Mock())]
        event = EndpointEvent(extension, status, calls)

        self.router.route(AGENT_ID, event)

        self.status_manager.device_in_use.assert_called_once_with(AGENT_ID, expected_direction, expected_is_internal)
