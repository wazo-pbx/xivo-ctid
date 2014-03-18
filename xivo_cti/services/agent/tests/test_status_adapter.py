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

from mock import Mock, patch
from xivo.asterisk.extension import Extension
from xivo_cti.services.agent.status_adapter import AgentStatusAdapter
from xivo_cti.services.agent.status_router import AgentStatusRouter
from xivo_cti.services.call.endpoint_notifier import EndpointNotifier
from xivo_cti.services.call.storage import Call
from xivo_cti.services.call.storage import CallStorage
from xivo_cti.model.endpoint_event import EndpointEvent
from xivo_cti.model.endpoint_status import EndpointStatus


def _create_extension(number, context):
    extension = Mock()
    extension.number = number
    extension.context = context

    return extension

AGENT_ID = 13
NUMBER = '1000'
CONTEXT = 'my_context'
EXTENSION = _create_extension(NUMBER, CONTEXT)


class TestStatusAdapter(unittest.TestCase):

    def setUp(self):
        self.endpoint_notifier = Mock(EndpointNotifier)
        self.call_storage = Mock(CallStorage)
        self.router = Mock(AgentStatusRouter)
        self.adapter = AgentStatusAdapter(self.router, self.endpoint_notifier, self.call_storage)

    @patch('xivo_dao.agent_status_dao.get_agent_id_from_extension')
    def test_handle_endpoint_event(self, get_agent_id_from_extension):
        status = EndpointStatus.talking
        calls = [Mock(Call)]
        event = EndpointEvent(EXTENSION, status, calls)
        get_agent_id_from_extension.return_value = AGENT_ID

        self.adapter.handle_endpoint_event(event)

        get_agent_id_from_extension.assert_called_once_with(NUMBER, CONTEXT)
        self.router.route.assert_called_once_with(AGENT_ID, event)

    @patch('xivo_dao.agent_status_dao.get_agent_id_from_extension')
    def test_handle_endpoint_event_with_no_agent(self, get_agent_id_from_extension):
        status = EndpointStatus.talking

        get_agent_id_from_extension.side_effect = LookupError()

        calls = [Mock(Call)]
        event = EndpointEvent(EXTENSION, status, calls)
        self._subscribe_to_event_for_agent(AGENT_ID, EXTENSION)

        self.adapter.handle_endpoint_event(event)

        self.assertEquals(self.router.route.call_count, 0)
        self.endpoint_notifier.unsubscribe_from_status_changes.assert_called_once_with(
            EXTENSION,
            self.adapter.handle_endpoint_event)

    @patch('xivo_dao.agent_status_dao.get_extension_from_agent_id')
    def test_subscribe_to_agent_events(self, get_extension_from_agent_id):
        status = EndpointStatus.talking
        calls = [Mock(Call)]
        extension = Extension(NUMBER, CONTEXT, is_internal=True)

        get_extension_from_agent_id.return_value = (NUMBER, CONTEXT)
        self.call_storage.get_status_for_extension.return_value = status
        self.call_storage.find_all_calls_for_extension.return_value = calls
        expected_event = EndpointEvent(extension, status, calls)

        self.adapter.subscribe_to_agent_events(AGENT_ID)

        get_extension_from_agent_id.assert_called_once_with(AGENT_ID)
        self.endpoint_notifier.subscribe_to_status_changes.assert_called_once_with(
            extension,
            self.adapter.handle_endpoint_event)
        self.router.route.assert_called_once_with(AGENT_ID, expected_event)

    @patch('xivo_dao.agent_status_dao.get_extension_from_agent_id', Mock(side_effect=LookupError))
    def test_subscribe_to_agent_events_with_no_agent(self):

        self.adapter.subscribe_to_agent_events(AGENT_ID)

        self.assertEquals(self.endpoint_notifier.subscribe_to_status_changes.call_count, 0)
        self.assertEquals(self.router.route.call_count, 0)

    def test_unsubscribe_from_agent_events(self):
        extension = Extension(NUMBER, CONTEXT, is_internal=True)
        self._subscribe_to_event_for_agent(AGENT_ID, extension)

        self.adapter.unsubscribe_from_agent_events(AGENT_ID)

        self.endpoint_notifier.unsubscribe_from_status_changes.assert_called_once_with(
            extension,
            self.adapter.handle_endpoint_event)

    def test_unsubscribe_from_agent_events_twice(self):
        extension = Extension(NUMBER, CONTEXT, is_internal=True)
        self._subscribe_to_event_for_agent(AGENT_ID, extension)

        self.adapter.unsubscribe_from_agent_events(AGENT_ID)
        self.adapter.unsubscribe_from_agent_events(AGENT_ID)

        self.endpoint_notifier.unsubscribe_from_status_changes.assert_called_once_with(
            extension,
            self.adapter.handle_endpoint_event)

    def test_unsubscribe_from_agent_events_if_not_subscribed(self):
        self.adapter.unsubscribe_from_agent_events(AGENT_ID)

        self.assertEquals(self.endpoint_notifier.unsubscribe_from_status_changes.call_count, 0)

    @patch('xivo_dao.agent_status_dao.get_logged_agent_ids')
    @patch('xivo_dao.agent_status_dao.get_extension_from_agent_id')
    def test_subscribe_all_logged_agents(self, get_extension_from_agent_id, get_logged_agent_ids):
        agent_id_1 = 13
        agent_id_2 = 72
        status_1 = EndpointStatus.talking
        status_2 = EndpointStatus.available
        agent_extension_1 = Extension('3543', 'my_context', is_internal=True)
        agent_extension_2 = Extension('6353', 'my_context', is_internal=True)
        calls_1 = [Mock(Call)]
        calls_2 = [Mock(Call), Mock(Call)]
        event_1 = EndpointEvent(agent_extension_1, status_1, calls_1)
        event_2 = EndpointEvent(agent_extension_2, status_2, calls_2)
        get_logged_agent_ids.return_value = [agent_id_1, agent_id_2]
        self.call_storage.get_status_for_extension.side_effect = [status_1, status_2]
        self.call_storage.find_all_calls_for_extension.side_effect = [calls_1, calls_2]
        get_extension_from_agent_id.side_effect = [(agent_extension_1.number, agent_extension_1.context),
                                                   (agent_extension_2.number, agent_extension_2.context)]

        self.adapter.subscribe_all_logged_agents()

        self.assertEquals(self.endpoint_notifier.subscribe_to_status_changes.call_count, 2)
        self.endpoint_notifier.subscribe_to_status_changes.assert_any_call(agent_extension_1, self.adapter.handle_endpoint_event)
        self.endpoint_notifier.subscribe_to_status_changes.assert_any_call(agent_extension_2, self.adapter.handle_endpoint_event)
        self.assertEquals(self.router.route.call_count, 2)
        self.router.route.assert_any_call(agent_id_1, event_1)
        self.router.route.assert_any_call(agent_id_2, event_2)

    @patch('xivo_dao.agent_status_dao.get_logged_agent_ids')
    @patch('xivo_dao.agent_status_dao.get_extension_from_agent_id')
    def test_subscribe_all_logged_agents_with_one_agent_then_unsubscribe(self, get_extension_from_agent_id, get_logged_agent_ids):
        status = EndpointStatus.talking
        calls = [Mock(Call)]
        agent_extension = Extension('3543', 'my_context', is_internal=True)
        get_logged_agent_ids.return_value = [AGENT_ID]
        self.call_storage.get_status_for_extension.return_value = status
        self.call_storage.find_all_calls_for_extension.return_value = calls
        event = EndpointEvent(agent_extension, status, calls)
        get_extension_from_agent_id.return_value = (agent_extension.number, agent_extension.context)

        self.adapter.subscribe_all_logged_agents()
        self.adapter.unsubscribe_from_agent_events(AGENT_ID)

        self.endpoint_notifier.subscribe_to_status_changes.assert_called_once_with(agent_extension, self.adapter.handle_endpoint_event)
        self.endpoint_notifier.unsubscribe_from_status_changes.assert_called_once_with(agent_extension, self.adapter.handle_endpoint_event)
        self.router.route.assert_called_once_with(AGENT_ID, event)

    @patch('xivo_dao.agent_status_dao.get_extension_from_agent_id')
    def _subscribe_to_event_for_agent(self, agent_id, extension, get_extension_from_agent_id):
        get_extension_from_agent_id.return_value = (extension.number, extension.context)
        self.adapter.subscribe_to_agent_events(agent_id)
        self.router.reset_mock()
