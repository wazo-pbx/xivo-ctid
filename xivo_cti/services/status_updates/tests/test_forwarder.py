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
from ..forwarder import _StatusListener
from ..forwarder import StatusNotifier
from ..forwarder import _new_agent_notifier
from ..forwarder import _new_endpoint_notifier
from ..forwarder import _new_user_notifier
from ..forwarder import CTIMessageFormatter
from ..forwarder import BusConfig
from hamcrest import assert_that
from hamcrest import equal_to
from mock import ANY
from mock import call
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
                                         self.agent_status_notifier,
                                         self.endpoint_status_notifier,
                                         self.user_status_notifier)

    @patch('xivo_cti.services.status_updates.forwarder._new_agent_notifier')
    @patch('xivo_cti.services.status_updates.forwarder._new_endpoint_notifier')
    @patch('xivo_cti.services.status_updates.forwarder._new_user_notifier')
    def test_forwarder_without_arguments(self, new_user_notifier, new_endpoint_notifier, new_agent_notifier):
        _forwarder = StatusForwarder(sentinel.cti_group_factory, sentinel.task_queue)

        new_endpoint_notifier.assert_called_once_with(sentinel.cti_group_factory)
        new_user_notifier.assert_called_once_with(sentinel.cti_group_factory)
        new_agent_notifier.assert_called_once_with(sentinel.cti_group_factory)

    def test_on_agent_status_update(self):
        xivo_id = 'ca7f87e9-c2c8-5fad-ba1b-c3140ebb9be3'
        agent_id = 42
        event = {
            'name': 'agent_status_update',
            'data': {
                'agent_id': agent_id,
                'xivo_id': xivo_id,
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
            'data': {
                'endpoint_id': endpoint_id,
                'xivo_id': xivo_id,
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
            'data': {
                'user_id': user_id,
                'xivo_id': xivo_id,
                'status': 'busy',
            }
        }

        self.forwarder.on_user_status_update(event)

        self.user_status_notifier.update.assert_called_once_with(
            (xivo_id, user_id), 'busy')

    @patch('xivo_cti.services.status_updates.forwarder.config', sentinel.config)
    @patch('xivo_cti.services.status_updates.forwarder.ThreadedStatusListener')
    def test_that_run_starts_a_listener_thread(self, ThreadedStatusListener):
        self.forwarder.run()

        ThreadedStatusListener.assert_called_once_with(sentinel.config, sentinel.task_queue, self.forwarder)


class TestStatusNotifier(unittest.TestCase):

    def setUp(self):
        self.message_factory = Mock()
        self.cti_group_factory = Mock()
        self.notifier = StatusNotifier(self.cti_group_factory, self.message_factory)

    def test_register(self):
        keys = [
            ('xivo-1', 1),
            ('xivo-1', 2),
            ('xivo-2', 1),
        ]
        connection = Mock()

        self.notifier.register(connection, keys)

        assert_that(self.cti_group_factory.new_cti_group.call_count, equal_to(3))

    def test_that_the_status_is_sent_on_registration(self):
        keys = [
            ('xivo-1', 1),
        ]
        connection_1 = Mock()

        self.notifier.register(connection_1, keys)
        self.notifier.update(keys[0], 1)

        connection_2 = Mock()

        self.notifier.register(connection_2, keys)

        connection_2.send_message.assert_called_once_with(self.message_factory.return_value)
        self.message_factory.assert_called_once_with(keys[0], 1)

    def test_unregister(self):
        # XXX find a test that is not a copy of the implementation...
        pass


class TestNewAgentNotifier(unittest.TestCase):

    @patch('xivo_cti.services.status_updates.forwarder.StatusNotifier')
    def test_that_the_cti_group_factory_is_forwarded(self, StatusNotifier):
        _notifier = _new_agent_notifier(sentinel.cti_group_factory)

        StatusNotifier.assert_called_once_with(sentinel.cti_group_factory, ANY)

    @patch('xivo_cti.services.status_updates.forwarder.StatusNotifier')
    def test_that_agent_status_update_is_injected(self, StatusNotifier):
        _notifier = _new_agent_notifier(sentinel.cti_group_factory)

        StatusNotifier.assert_called_once_with(ANY, CTIMessageFormatter.agent_status_update)


class TestNewEndpointNotifier(unittest.TestCase):

    @patch('xivo_cti.services.status_updates.forwarder.StatusNotifier')
    def test_that_the_cti_group_factory_is_forwarded(self, StatusNotifier):
        _notifier = _new_endpoint_notifier(sentinel.cti_group_factory)

        StatusNotifier.assert_called_once_with(sentinel.cti_group_factory, ANY)

    @patch('xivo_cti.services.status_updates.forwarder.StatusNotifier')
    def test_that_endpoint_status_update_is_injected(self, StatusNotifier):
        _notifier = _new_endpoint_notifier(sentinel.cti_group_factory)

        StatusNotifier.assert_called_once_with(ANY, CTIMessageFormatter.endpoint_status_update)


class TestNewUserNotifier(unittest.TestCase):

    @patch('xivo_cti.services.status_updates.forwarder.StatusNotifier')
    def test_that_the_cti_group_factory_is_forwarded(self, StatusNotifier):
        _notifier = _new_endpoint_notifier(sentinel.cti_group_factory)

        StatusNotifier.assert_called_once_with(sentinel.cti_group_factory, ANY)

    @patch('xivo_cti.services.status_updates.forwarder.StatusNotifier')
    def test_that_user_status_update_is_injected(self, StatusNotifier):
        _notifier = _new_user_notifier(sentinel.cti_group_factory)

        StatusNotifier.assert_called_once_with(ANY, CTIMessageFormatter.user_status_update)


@patch('xivo_cti.services.status_updates.forwarder.BusConsumer')
class TestStatusListener(unittest.TestCase):

    def setUp(self):
        self.config = {
            'bus': {
                'host': 'example.com',
                'port': 5496,
                'username': 'u1',
                'password': 'secret',
                'exchange_name': 'xivo',
                'exchange_type': 'topic',
                'exchange_durable': True,
                'routing_keys': {
                    'user_status': 'status.user',
                    'endpoint_status': 'status.endpoint',
                    'agent_status': 'status.agent',
                },
            },
        }

        self.task_queue = Mock()
        self.forwarder = StatusForwarder(sentinel.cti_group_factory, sentinel.task_queue, Mock(), Mock(), Mock())

    def test_that_listener_instantiate_a_bus_consumer(self, BusConsumer):
        self.listener = _StatusListener(self.config, self.task_queue, self.forwarder)

        expected_config = BusConfig(
            host='example.com',
            port=5496,
            username='u1',
            password='secret',
            exchange_name='xivo',
            exchange_type='topic',
            exchange_durable=True,
        )
        BusConsumer.assert_called_once_with(expected_config)

    def test_that_listener_instantiate_adds_agent_cb(self, BusConsumer):
        self.listener = _StatusListener(self.config, self.task_queue, self.forwarder)

        consumer = BusConsumer.return_value

        expected_call = call(
            self.listener.queue_agent_status_update,
            'agent-status-updates',
            'xivo',
            'status.agent',
        )
        assert_that(expected_call in consumer.add_binding.mock_calls)

    def test_that_listener_instantiate_adds_endpoint_cb(self, BusConsumer):
        self.listener = _StatusListener(self.config, self.task_queue, self.forwarder)

        consumer = BusConsumer.return_value

        expected_call = call(
            self.listener.queue_endpoint_status_update,
            'endpoint-status-updates',
            'xivo',
            'status.endpoint',
        )
        assert_that(expected_call in consumer.add_binding.mock_calls)

    def test_that_listener_instantiate_adds_users_cb_to_the_forwarder(self, BusConsumer):
        self.listener = _StatusListener(self.config, self.task_queue, self.forwarder)

        consumer = BusConsumer.return_value

        expected_call = call(
            self.listener.queue_user_status_update,
            'user-status-updates',
            'xivo',
            'status.user',
        )
        assert_that(expected_call in consumer.add_binding.mock_calls)

    def test_that_listener_connect_and_run(self, BusConsumer):
        self.listener = _StatusListener(self.config, self.task_queue, self.forwarder)

        consumer = BusConsumer.return_value

        consumer.connect.assert_called_once_with()
        consumer.run.assert_called_once_with()

    def test_that_queue_agent_status_update_queues_a_task(self, _BusConsumer):
        self.listener = _StatusListener(self.config, self.task_queue, self.forwarder)

        self.listener.queue_agent_status_update(sentinel.event)

        self.task_queue.put.assert_called_once_with(self.forwarder.on_agent_status_update, sentinel.event)

    def test_that_queue_endpoint_status_update_queues_a_task(self, _BusConsumer):
        self.listener = _StatusListener(self.config, self.task_queue, self.forwarder)

        self.listener.queue_endpoint_status_update(sentinel.event)

        self.task_queue.put.assert_called_once_with(self.forwarder.on_endpoint_status_update, sentinel.event)

    def test_that_queue_user_status_update_queues_a_task(self, _BusConsumer):
        self.listener = _StatusListener(self.config, self.task_queue, self.forwarder)

        self.listener.queue_user_status_update(sentinel.event)

        self.task_queue.put.assert_called_once_with(self.forwarder.on_user_status_update, sentinel.event)
