# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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

from ..forwarder import StatusForwarder
from ..forwarder import _new_agent_notifier
from ..forwarder import _new_endpoint_notifier
from ..forwarder import _new_user_notifier
from ..forwarder import CTIMessageFormatter
from ..forwarder import _EndpointStatusFetcher

from mock import ANY
from mock import Mock
from mock import patch
from mock import sentinel


class TestStatusForwarder(unittest.TestCase):

    def setUp(self):
        self.agent_status_notifier = Mock()
        self.endpoint_status_notifier = Mock()
        self.user_status_notifier = Mock()
        self.forwarder = StatusForwarder(sentinel.cti_group_factory,
                                         sentinel.task_queue,
                                         sentinel.bus_connection,
                                         sentinel.bus_exchange,
                                         self.agent_status_notifier,
                                         self.endpoint_status_notifier,
                                         self.user_status_notifier)

    @patch('xivo_cti.services.status_updates.forwarder._new_agent_notifier')
    @patch('xivo_cti.services.status_updates.forwarder._new_endpoint_notifier')
    @patch('xivo_cti.services.status_updates.forwarder._new_user_notifier')
    def test_forwarder_without_arguments(self, new_user_notifier, new_endpoint_notifier, new_agent_notifier):
        StatusForwarder(sentinel.cti_group_factory, sentinel.task_queue,
                        sentinel.bus_connection, sentinel.bus_exchange)

        new_endpoint_notifier.assert_called_once_with(sentinel.cti_group_factory)
        new_user_notifier.assert_called_once_with(sentinel.cti_group_factory)
        new_agent_notifier.assert_called_once_with(sentinel.cti_group_factory)

    def test_on_agent_status_update(self):
        xivo_id = 'ca7f87e9-c2c8-5fad-ba1b-c3140ebb9be3'
        agent_id = 42
        event = {
            'name': 'agent_status_update',
            'origin_uuid': xivo_id,
            'data': {
                'agent_id': agent_id,
                'status': 'logged_in',
            }
        }

        self.forwarder.on_agent_status_update(event)

        self.agent_status_notifier.update.assert_called_once_with(
            (xivo_id, agent_id), 'logged_in')

    def test_on_endpoint_status_update(self):
        xivo_id = 'ca7f87e9-c2c8-5fad-ba1b-c3140ebb9be3'
        endpoint_id = 67
        event = {
            'name': 'endpoint_status_update',
            'origin_uuid': xivo_id,
            'data': {
                'endpoint_id': endpoint_id,
                'status': 0,
            }
        }

        self.forwarder.on_endpoint_status_update(event)

        self.endpoint_status_notifier.update.assert_called_once_with(
            (xivo_id, endpoint_id), 0)

    def test_on_user_status_update(self):
        xivo_id = 'ca7f87e9-c2c8-5fad-ba1b-c3140ebb9be3'
        user_id = 67
        event = {
            'name': 'user_status_update',
            'origin_uuid': xivo_id,
            'data': {
                'user_id': user_id,
                'status': 'busy',
            }
        }

        self.forwarder.on_user_status_update(event)

        self.user_status_notifier.update.assert_called_once_with(
            (xivo_id, user_id), 'busy')

    @patch('xivo_cti.services.status_updates.forwarder.config', sentinel.config)
    @patch('xivo_cti.services.status_updates.forwarder._ThreadedStatusListener')
    def test_that_run_starts_a_listener_thread(self, _ThreadedStatusListener):
        self.forwarder.run()

        _ThreadedStatusListener.assert_called_once_with(sentinel.config, sentinel.task_queue,
                                                        sentinel.bus_connection, self.forwarder,
                                                        sentinel.bus_exchange)


class TestNewAgentNotifier(unittest.TestCase):

    @patch('xivo_cti.services.status_updates.forwarder._StatusNotifier')
    def test_that_the_cti_group_factory_is_forwarded(self, _StatusNotifier):
        _new_agent_notifier(sentinel.cti_group_factory)

        _StatusNotifier.assert_called_once_with(sentinel.cti_group_factory, ANY)

    @patch('xivo_cti.services.status_updates.forwarder._StatusNotifier')
    def test_that_agent_status_update_is_injected(self, _StatusNotifier):
        _new_agent_notifier(sentinel.cti_group_factory)

        _StatusNotifier.assert_called_once_with(ANY, CTIMessageFormatter.agent_status_update)


class TestNewEndpointNotifier(unittest.TestCase):

    @patch('xivo_cti.services.status_updates.forwarder._StatusNotifier')
    def test_that_the_cti_group_factory_is_forwarded(self, _StatusNotifier):
        _new_endpoint_notifier(sentinel.cti_group_factory)

        _StatusNotifier.assert_called_once_with(sentinel.cti_group_factory, ANY)

    @patch('xivo_cti.services.status_updates.forwarder._StatusNotifier')
    def test_that_endpoint_status_update_is_injected(self, _StatusNotifier):
        _new_endpoint_notifier(sentinel.cti_group_factory)

        _StatusNotifier.assert_called_once_with(ANY, CTIMessageFormatter.endpoint_status_update)


class TestNewUserNotifier(unittest.TestCase):

    @patch('xivo_cti.services.status_updates.forwarder._StatusNotifier')
    def test_that_the_cti_group_factory_is_forwarded(self, _StatusNotifier):
        _new_endpoint_notifier(sentinel.cti_group_factory)

        _StatusNotifier.assert_called_once_with(sentinel.cti_group_factory, ANY)

    @patch('xivo_cti.services.status_updates.forwarder._StatusNotifier')
    def test_that_user_status_update_is_injected(self, _StatusNotifier):
        _new_user_notifier(sentinel.cti_group_factory)

        _StatusNotifier.assert_called_once_with(ANY, CTIMessageFormatter.user_status_update)


class TestEndpointStatusFetcher(unittest.TestCase):

    def setUp(self):
        self.uuid = 'some-uuid'
        self.id_ = 42
        self.key = (self.uuid, self.id_)

    def test_that_on_response_calls_the_forwarder(self):
        forwarder = Mock(StatusForwarder)

        fetcher = _EndpointStatusFetcher(forwarder)

        fetcher._on_result({
            'id': self.id_,
            'origin_uuid': self.uuid,
            'status': 8,
        })

        forwarder.on_endpoint_status_update.assert_called_once_with(self.key, 8)

    @patch('xivo_cti.services.status_updates.forwarder.CtidClient')
    def test_that_fetch_get_from_a_client(self, CtidClient):
        client = CtidClient.return_value = Mock()
        forwarder = Mock(StatusForwarder)

        fetcher = _EndpointStatusFetcher(forwarder)
        fetcher._get_client_config = Mock(return_value={'host': 'localhost', 'port': 6666})
        fetcher._on_result = Mock()

        fetcher.fetch(self.key)

        fetcher._get_client_config.assert_called_once_with(self.uuid)
        CtidClient.assert_called_once_with(host='localhost', port=6666)
        client.endpoints.get.assert_called_once_with(self.id_)
