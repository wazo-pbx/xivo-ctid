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


from concurrent import futures
from hamcrest import assert_that, equal_to
from mock import ANY
from mock import Mock
from mock import patch
from mock import sentinel as s

from xivo_cti.async_runner import AsyncRunner, synchronize
from xivo_cti.task_queue import new_task_queue

from ..forwarder import StatusForwarder
from ..forwarder import _new_agent_notifier
from ..forwarder import _new_endpoint_notifier
from ..forwarder import _new_user_notifier
from ..forwarder import CTIMessageFormatter
from ..forwarder import _EndpointStatusFetcher


class TestStatusForwarder(unittest.TestCase):

    def setUp(self):
        self.agent_status_notifier = Mock()
        self.endpoint_status_notifier = Mock()
        self.user_status_notifier = Mock()
        self.forwarder = StatusForwarder(s.cti_group_factory,
                                         s.task_queue,
                                         s.bus_connection,
                                         s.bus_exchange,
                                         s.async_runner,
                                         self.agent_status_notifier,
                                         self.endpoint_status_notifier,
                                         self.user_status_notifier)

    @patch('xivo_cti.services.status_updates.forwarder._new_agent_notifier')
    @patch('xivo_cti.services.status_updates.forwarder._new_endpoint_notifier')
    @patch('xivo_cti.services.status_updates.forwarder._new_user_notifier')
    def test_forwarder_without_arguments(self, new_user_notifier, new_endpoint_notifier, new_agent_notifier):
        StatusForwarder(s.cti_group_factory,
                        s.task_queue,
                        s.bus_connection,
                        s.bus_exchange,
                        s.async_runner)

        assert_that(new_endpoint_notifier.call_count, equal_to(1))
        assert_that(new_user_notifier.call_count, equal_to(1))
        assert_that(new_agent_notifier.call_count, equal_to(1))

    def test_on_agent_status_update(self):
        xivo_id = 'ca7f87e9-c2c8-5fad-ba1b-c3140ebb9be3'
        agent_id = 42
        status = 'logged_in'

        self.forwarder.on_agent_status_update((xivo_id, agent_id), status)

        self.agent_status_notifier.update.assert_called_once_with(
            (xivo_id, agent_id), 'logged_in')

    def test_on_endpoint_status_update(self):
        xivo_id = 'ca7f87e9-c2c8-5fad-ba1b-c3140ebb9be3'
        endpoint_id = 67
        status = 0

        self.forwarder.on_endpoint_status_update((xivo_id, endpoint_id), status)

        self.endpoint_status_notifier.update.assert_called_once_with(
            (xivo_id, endpoint_id), 0)

    def test_on_user_status_update(self):
        xivo_id = 'ca7f87e9-c2c8-5fad-ba1b-c3140ebb9be3'
        user_id = 67
        status = 'busy'

        self.forwarder.on_user_status_update((xivo_id, user_id), status)

        self.user_status_notifier.update.assert_called_once_with(
            (xivo_id, user_id), 'busy')

    @patch('xivo_cti.services.status_updates.forwarder._ThreadedStatusListener')
    def test_that_run_starts_a_listener_thread(self, _ThreadedStatusListener):
        self.forwarder.run()

        _ThreadedStatusListener.assert_called_once_with(s.task_queue,
                                                        s.bus_connection, self.forwarder,
                                                        s.bus_exchange)


class TestNewAgentNotifier(unittest.TestCase):

    @patch('xivo_cti.services.status_updates.forwarder._StatusNotifier')
    def test_that_the_cti_group_factory_is_forwarded(self, _StatusNotifier):
        _new_agent_notifier(s.cti_group_factory)

        _StatusNotifier.assert_called_once_with(s.cti_group_factory, ANY, None)

    @patch('xivo_cti.services.status_updates.forwarder._StatusNotifier')
    def test_that_agent_status_update_is_injected(self, _StatusNotifier):
        _new_agent_notifier(s.cti_group_factory)

        _StatusNotifier.assert_called_once_with(ANY, CTIMessageFormatter.agent_status_update, None)


class TestNewEndpointNotifier(unittest.TestCase):

    @patch('xivo_cti.services.status_updates.forwarder._StatusNotifier')
    def test_that_the_cti_group_factory_is_forwarded(self, _StatusNotifier):
        _new_endpoint_notifier(s.cti_group_factory, s.fetcher)

        _StatusNotifier.assert_called_once_with(s.cti_group_factory, ANY, s.fetcher)

    @patch('xivo_cti.services.status_updates.forwarder._StatusNotifier')
    def test_that_endpoint_status_update_is_injected(self, _StatusNotifier):
        _new_endpoint_notifier(s.cti_group_factory, s.fetcher)

        _StatusNotifier.assert_called_once_with(ANY, CTIMessageFormatter.endpoint_status_update, s.fetcher)


class TestNewUserNotifier(unittest.TestCase):

    @patch('xivo_cti.services.status_updates.forwarder._StatusNotifier')
    def test_that_the_cti_group_factory_is_forwarded(self, _StatusNotifier):
        _new_user_notifier(s.cti_group_factory, s.fetcher)

        _StatusNotifier.assert_called_once_with(s.cti_group_factory, ANY, s.fetcher)

    @patch('xivo_cti.services.status_updates.forwarder._StatusNotifier')
    def test_that_user_status_update_is_injected(self, _StatusNotifier):
        _new_user_notifier(s.cti_group_factory, s.fetcher)

        _StatusNotifier.assert_called_once_with(ANY, CTIMessageFormatter.user_status_update, s.fetcher)


class TestEndpointStatusFetcher(unittest.TestCase):

    def setUp(self):
        self.uuid = 'some-uuid'
        self.id_ = 42
        self.key = (self.uuid, self.id_)
        self.async_runner = AsyncRunner(futures.ThreadPoolExecutor(max_workers=1), new_task_queue())

    def test_that_on_response_calls_the_forwarder(self):
        forwarder = Mock(StatusForwarder)

        fetcher = _EndpointStatusFetcher(forwarder, self.async_runner)

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

        fetcher = _EndpointStatusFetcher(forwarder, self.async_runner)
        fetcher._get_client_config = Mock(return_value={'host': 'localhost', 'port': 6666})
        fetcher._on_result = Mock()

        with synchronize(self.async_runner):
            fetcher.fetch(self.key)

        fetcher._get_client_config.assert_called_once_with(self.uuid)
        CtidClient.assert_called_once_with(host='localhost', port=6666)
        client.endpoints.get.assert_called_once_with(self.id_)
