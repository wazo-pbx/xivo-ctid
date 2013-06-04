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
from xivo.asterisk.extension import Extension
from xivo_cti.services.agent.status_adapter import AgentStatusAdapter
from xivo_cti.services.agent.status_router import AgentStatusRouter
from xivo_cti.model.call_event import CallEvent
from xivo_cti.services.call.notifier import CallNotifier
from xivo_cti.services.call.storage import CallStorage
from xivo_cti.model.endpoint_status import EndpointStatus


class TestStatusAdapter(unittest.TestCase):

    def setUp(self):
        self.call_notifier = Mock(CallNotifier)
        self.call_storage = Mock(CallStorage)
        self.router = Mock(AgentStatusRouter)
        self.adapter = AgentStatusAdapter(self.router, self.call_notifier, self.call_storage)

    @patch('xivo_dao.agent_status_dao.get_agent_id_from_extension')
    def test_handle_call_event(self, get_agent_id_from_extension):
        agent_id = 1
        extension = Extension('1000', 'default')
        status = EndpointStatus.talking

        event = Mock(CallEvent)
        event.extension = extension
        event.status = status

        get_agent_id_from_extension.return_value = agent_id

        self.adapter.handle_call_event(event)

        get_agent_id_from_extension.assert_called_once_with(extension.number, extension.context)
        self.router.route.assert_called_once_with(agent_id, status)

    @patch('xivo_dao.agent_status_dao.get_agent_id_from_extension')
    def test_handle_call_event_with_no_agent(self, get_agent_id_from_extension):
        agent_id = 24
        extension = Extension('1000', 'default')
        status = EndpointStatus.talking

        get_agent_id_from_extension.side_effect = LookupError()

        event = Mock(CallEvent)
        event.extension = extension
        event.status = status
        self._subscribe_to_event_for_agent(agent_id, extension)
        self.router.reset_mock()

        self.adapter.handle_call_event(event)

        self.assertEquals(self.router.route.call_count, 0)
        self.call_notifier.unsubscribe_from_status_changes.assert_called_once_with(
            extension,
            self.adapter.handle_call_event)

    @patch('xivo_dao.agent_status_dao.get_extension_from_agent_id')
    def test_subscribe_to_agent_events(self, get_extension_from_agent_id):
        agent_id = 1
        extension = Extension('1000', 'default')
        status = EndpointStatus.talking

        get_extension_from_agent_id.return_value = (extension.number, extension.context)
        self.call_storage.get_status_for_extension.return_value = status

        self.adapter.subscribe_to_agent_events(agent_id)

        get_extension_from_agent_id.assert_called_once_with(agent_id)
        self.call_notifier.subscribe_to_status_changes.assert_called_once_with(
            extension,
            self.adapter.handle_call_event)
        self.router.route.assert_called_once_with(agent_id, status)

    @patch('xivo_dao.agent_status_dao.get_extension_from_agent_id', Mock(side_effect=LookupError))
    def test_subscribe_to_agent_events_with_no_agent(self):
        agent_id = 1

        self.adapter.subscribe_to_agent_events(agent_id)

        self.assertEquals(self.call_notifier.subscribe_to_status_changes.call_count, 0)

    def test_unsubscribe_from_agent_events(self):
        agent_id = 29
        extension = Extension('1000', 'default')
        self._subscribe_to_event_for_agent(agent_id, extension)

        self.adapter.unsubscribe_from_agent_events(agent_id)

        self.call_notifier.unsubscribe_from_status_changes.assert_called_once_with(
            extension,
            self.adapter.handle_call_event)

    def test_unsubscribe_from_agent_events_twice(self):
        agent_id = 29
        extension = Extension('1000', 'default')
        self._subscribe_to_event_for_agent(agent_id, extension)

        self.adapter.unsubscribe_from_agent_events(agent_id)
        self.adapter.unsubscribe_from_agent_events(agent_id)

        self.call_notifier.unsubscribe_from_status_changes.assert_called_once_with(
            extension,
            self.adapter.handle_call_event)

    def test_unsubscribe_from_agent_events_if_not_subscribed(self):
        agent_id = 29

        self.adapter.unsubscribe_from_agent_events(agent_id)

        self.assertEquals(self.call_notifier.unsubscribe_from_status_changes.call_count, 0)

    @patch('xivo_dao.agent_status_dao.get_logged_agent_ids')
    @patch('xivo_dao.agent_status_dao.get_extension_from_agent_id')
    def test_subscribe_all_logged_agents(self, get_extension_from_agent_id, get_logged_agent_ids):
        agent_id_1 = 13
        agent_id_2 = 72
        status_1 = EndpointStatus.talking
        status_2 = EndpointStatus.available
        agent_extension_1 = Extension('624', 'default')
        agent_extension_2 = Extension('635', 'my_context')
        get_logged_agent_ids.return_value = [agent_id_1, agent_id_2]
        self.call_storage.get_status_for_extension.side_effect = [status_1, status_2]
        get_extension_from_agent_id.side_effect = [(agent_extension_1.number, agent_extension_1.context),
                                                   (agent_extension_2.number, agent_extension_2.context)]

        self.adapter.subscribe_all_logged_agents()

        self.assertEquals(self.call_notifier.subscribe_to_status_changes.call_count, 2)
        self.call_notifier.subscribe_to_status_changes.assert_any_call(agent_extension_1, self.adapter.handle_call_event)
        self.call_notifier.subscribe_to_status_changes.assert_any_call(agent_extension_2, self.adapter.handle_call_event)
        self.assertEquals(self.router.route.call_count, 2)
        self.router.route.assert_any_call(agent_id_1, status_1)
        self.router.route.assert_any_call(agent_id_2, status_2)

    @patch('xivo_dao.agent_status_dao.get_logged_agent_ids')
    @patch('xivo_dao.agent_status_dao.get_extension_from_agent_id')
    def test_subscribe_all_logged_agents_with_one_agent_then_unsubscribe(self, get_extension_from_agent_id, get_logged_agent_ids):
        agent_id = 13
        status = EndpointStatus.talking
        agent_extension = Extension('624', 'default')
        get_logged_agent_ids.return_value = [agent_id]
        self.call_storage.get_status_for_extension.return_value = status
        get_extension_from_agent_id.return_value = (agent_extension.number, agent_extension.context)

        self.adapter.subscribe_all_logged_agents()
        self.adapter.unsubscribe_from_agent_events(agent_id)

        self.call_notifier.subscribe_to_status_changes.assert_called_once_with(agent_extension, self.adapter.handle_call_event)
        self.call_notifier.unsubscribe_from_status_changes.assert_called_once_with(agent_extension, self.adapter.handle_call_event)
        self.router.route.assert_called_once_with(agent_id, status)

    @patch('xivo_dao.agent_status_dao.get_extension_from_agent_id')
    def _subscribe_to_event_for_agent(self, agent_id, extension, get_extension_from_agent_id):
        get_extension_from_agent_id.return_value = (extension.number, extension.context)
        self.adapter.subscribe_to_agent_events(agent_id)
