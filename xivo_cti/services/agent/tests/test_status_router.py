# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock
from mock import sentinel
from xivo.asterisk.extension import Extension
from xivo_cti.services.agent.status_manager import AgentStatusManager
from xivo_cti.services.agent.status_router import AgentStatusRouter
from xivo_cti.services.call.direction import CallDirection
from xivo_cti.services.call.storage import Call
from xivo_cti.services.call.call import _Channel
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
        extension = Extension(number=NUMBER, context=CONTEXT, is_internal=is_internal)
        expected_direction = CallDirection.incoming
        expected_is_internal = is_internal
        status = EndpointStatus.talking
        source_channel = _Channel(Mock(Extension, is_internal=True), sentinel.source_channel)
        destination_channel = _Channel(extension, sentinel.destination_channel)
        calls = [Call(source_channel, destination_channel)]
        event = EndpointEvent(extension, status, calls)

        self.router.route(AGENT_ID, event)

        self.status_manager.device_in_use.assert_called_once_with(AGENT_ID, expected_direction, expected_is_internal)

    def test_route_device_in_use_outgoing_external(self):
        is_internal = False
        extension = Extension(number=NUMBER, context=CONTEXT, is_internal=is_internal)
        expected_is_internal = is_internal
        expected_direction = CallDirection.outgoing
        status = EndpointStatus.talking
        source_channel = _Channel(extension, sentinel.source_channel)
        destination_channel = _Channel(Mock(Extension), sentinel.destination_channel)
        calls = [Call(source_channel, destination_channel)]
        event = EndpointEvent(extension, status, calls)

        self.router.route(AGENT_ID, event)

        self.status_manager.device_in_use.assert_called_once_with(AGENT_ID, expected_direction, expected_is_internal)
