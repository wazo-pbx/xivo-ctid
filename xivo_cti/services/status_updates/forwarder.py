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

import logging
import json
import threading
import xivo_agentd_client

from collections import defaultdict
from functools import wraps

from kombu.mixins import ConsumerMixin
from kombu import Queue

from xivo_ctid_client import Client as CtidClient

from xivo_bus.resources.cti.event import AgentStatusUpdateEvent,\
    UserStatusUpdateEvent, EndpointStatusUpdateEvent
from xivo_cti import config
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter
from xivo_cti.remote_service import RemoteService

logger = logging.getLogger(__name__)


class StatusForwarder(object):

    def __init__(self,
                 cti_group_factory,
                 task_queue,
                 bus_connection,
                 bus_exchange,
                 async_runner,
                 remote_service_tracker,
                 _agent_status_notifier=None,
                 _endpoint_status_notifier=None,
                 _user_status_notifier=None):
        agent_status_fetcher = _AgentStatusFetcher(self, async_runner, remote_service_tracker)
        endpoint_status_fetcher = _EndpointStatusFetcher(self, async_runner, remote_service_tracker)
        user_status_fetcher = _UserStatusFetcher(self, async_runner, remote_service_tracker)
        self._task_queue = task_queue
        self._exchange = bus_exchange
        self._bus_connection = bus_connection
        self.agent_status_notifier = _agent_status_notifier or _new_agent_notifier(cti_group_factory, agent_status_fetcher)
        self.endpoint_status_notifier = _endpoint_status_notifier or _new_endpoint_notifier(cti_group_factory, endpoint_status_fetcher)
        self.user_status_notifier = _user_status_notifier or _new_user_notifier(cti_group_factory, user_status_fetcher)
        self._remote_service_tracker = remote_service_tracker

    def run(self):
        self._listener = _ThreadedStatusListener(self._task_queue,
                                                 self._bus_connection,
                                                 self,
                                                 self._exchange,
                                                 self._remote_service_tracker)

    def stop(self):
        self._listener.stop()

    def on_agent_status_update(self, key, status):
        self.agent_status_notifier.update(key, status)

    def on_endpoint_status_update(self, key, status):
        self.endpoint_status_notifier.update(key, status)

    def on_user_status_update(self, key, status):
        self.user_status_notifier.update(key, status)

    def on_service_added(self, service_name, uuid):
        if service_name == 'xivo-ctid':
            self.endpoint_status_notifier.on_service_started(uuid)
            self.user_status_notifier.on_service_started(uuid)


class _ThreadedStatusListener(object):

    def __init__(self, task_queue, connection, forwarder, exchange, remote_service_tracker):
        self._listener = _StatusListener(task_queue, connection, forwarder, exchange, remote_service_tracker)
        self._thread = threading.Thread(target=self._listener.start)
        self._thread.start()

    def stop(self):
        self._listener.stop()
        self._thread.join()


def _loads_and_ack(f):
    @wraps(f)
    def wrapped(one_self, body, message):
        f(one_self, json.loads(body))
        message.ack()
    return wrapped


class _StatusWorker(ConsumerMixin):

    _id_field_map = {
        'agent_status_update': 'agent_id',
        'endpoint_status_update': 'endpoint_id',
        'user_status_update': 'user_id',
    }

    def __init__(self, connection, exchange, task_queue, forwarder, remote_service_tracker):
        self.connection = connection
        self.exchange = exchange
        self._task_queue = task_queue
        self._forwarder = forwarder
        self._remote_service_tracker = remote_service_tracker
        self._agent_queue = self._make_queue(AgentStatusUpdateEvent.routing_key)
        self._user_queue = self._make_queue(UserStatusUpdateEvent.routing_key)
        self._endpoint_queue = self._make_queue(EndpointStatusUpdateEvent.routing_key)
        self._service_registered_queue = self._make_queue('service.registered.#')
        self._service_deregistered_queue = self._make_queue('service.deregistered.#')

    def _make_queue(self, routing_key):
        return Queue(exchange=self.exchange, routing_key=routing_key, exclusive=True)

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=self._agent_queue,
                         callbacks=[self._on_agent_status]),
                Consumer(queues=self._user_queue,
                         callbacks=[self._on_user_status]),
                Consumer(queues=self._endpoint_queue,
                         callbacks=[self._on_endpoint_status]),
                Consumer(queues=self._service_registered_queue,
                         callbacks=[self._on_service_registered]),
                Consumer(queues=self._service_deregistered_queue,
                         callbacks=[self._on_service_deregistered])]

    def _extract_key(self, event):
        id_field = self._id_field_map[event['name']]
        return event['origin_uuid'], event['data'][id_field]

    # All methods below this line are executed in the status listener's thread
    @_loads_and_ack
    def _on_service_registered(self, body):
        service = RemoteService.from_bus_msg(body)
        uuid = body['origin_uuid']
        service_name = body['data']['service_name']
        self._task_queue.put(self._remote_service_tracker.add_service_node,
                             service_name, uuid, service)
        self._task_queue.put(self._forwarder.on_service_added, service_name, uuid)

    @_loads_and_ack
    def _on_service_deregistered(self, body):
        uuid = body['origin_uuid']
        service_name = body['data']['service_name']
        service_id = body['data']['service_id']
        self._task_queue.put(self._remote_service_tracker.remove_service_node,
                             service_name, service_id, uuid)

    @_loads_and_ack
    def _on_agent_status(self, body):
        key = self._extract_key(body)
        status = body['data']['status']
        self._task_queue.put(self._forwarder.on_agent_status_update, key, status)

    @_loads_and_ack
    def _on_user_status(self, body):
        key = self._extract_key(body)
        status = body['data']['status']
        self._task_queue.put(self._forwarder.on_user_status_update, key, status)

    @_loads_and_ack
    def _on_endpoint_status(self, body):
        key = self._extract_key(body)
        status = body['data']['status']
        self._task_queue.put(self._forwarder.on_endpoint_status_update, key, status)


class _StatusListener(object):

    def __init__(self, task_queue, connection, forwarder, exchange, remote_service_tracker):
        self._worker = _StatusWorker(connection, exchange, task_queue, forwarder, remote_service_tracker)

    def start(self):
        self._worker.run()

    def stop(self):
        self._worker.should_stop = True


class _StatusNotifier(object):

    def __init__(self, cti_group_factory, message_factory, fetcher, resource_name):
        self._subscriptions = defaultdict(lambda: defaultdict(cti_group_factory.new_cti_group))
        self._message_factory = message_factory
        self._statuses = {}
        self._fetcher = fetcher
        self._resource_name = resource_name

    def on_service_started(self, uuid):
        if not self._fetcher:
            return

        keys_on_service = [(uuid, resource_id) for resource_id in self._subscriptions[uuid].iterkeys()]
        missing_statuses = [key for key in keys_on_service if key not in self._statuses]

        logger.debug('%s notifier: new service detected, fetching %s', self._resource_name, missing_statuses)
        for key in missing_statuses:
            self._fetcher.fetch(key)

    def register(self, connection, keys):
        for key in keys:
            logger.debug('registering to %s: %s', self._resource_name, key)
            xivo_uuid, resource_id = key
            self._subscriptions[xivo_uuid][resource_id].add(connection)
            status_msg = self._statuses.get(key)
            if status_msg:
                connection.send_message(status_msg)
            elif self._fetcher:
                self._fetcher.fetch(key)

    def unregister(self, connection, keys):
        for key in keys:
            xivo_uuid, resource_id = key
            self._subscriptions[xivo_uuid][resource_id].remove(connection)

    def update(self, key, new_status):
        msg = self._message_factory(key, new_status)
        self._statuses[key] = msg

        xivo_uuid, resource_id = key
        subscription = self._subscriptions[xivo_uuid].get(resource_id)
        if subscription is None:
            logger.debug('No subscriptions for %s in %s', key, self._subscriptions.keys())
            return

        subscription.send_message(msg)


class _BaseStatusFetcher(object):

    def __init__(self, status_forwarder, async_runner, remote_service_tracker):
        self.forwarder = status_forwarder
        self.async_runner = async_runner
        self._remote_service_tracker = remote_service_tracker

    def _get_agentd_client_config(self, uuid):
        if uuid == config['uuid']:
            return config['agentd']
        return None

    def _get_ctid_client_config(self, uuid):
        for service in self._remote_service_tracker.list_services_with_uuid('xivo-ctid', uuid):
            return service.to_dict()
        return None


class _AgentStatusFetcher(_BaseStatusFetcher):

    def fetch(self, key):
        logger.debug('Fetching agent %s', key)
        uuid, agent_id = key
        if not agent_id:
            return
        client_config = self._get_agentd_client_config(uuid)
        if not client_config:
            logger.warning('Could not fetch agent %s on %s, unknown uuid', agent_id, uuid)
            return

        client = xivo_agentd_client.Client(**client_config)
        self.async_runner.run_with_cb(self._on_result, client.agents.get_agent_status, agent_id)

    def _on_result(self, result):
        key = result.origin_uuid, result.id
        status = 'logged_in' if result.logged else 'logged_out'

        self.forwarder.on_agent_status_update(key, status)


class _EndpointStatusFetcher(_BaseStatusFetcher):

    def fetch(self, key):
        uuid, endpoint_id = key
        client_config = self._get_ctid_client_config(uuid)
        if not client_config:
            logger.warning('Could not fetch endpoint %s on %s, unknown uuid', endpoint_id, uuid)
            return

        client = CtidClient(**client_config)
        logger.debug('endpoint fetcher: scheduling a client.endpoints.get with %s for endpoint %s on %s',
                     client_config, endpoint_id, uuid)
        self.async_runner.run_with_cb(self._on_result, client.endpoints.get, endpoint_id)

    def _on_result(self, result):
        key = result['origin_uuid'], result['id']
        status = result['status']

        self.forwarder.on_endpoint_status_update(key, status)


class _UserStatusFetcher(_BaseStatusFetcher):

    def fetch(self, key):
        uuid, user_id = key
        client_config = self._get_ctid_client_config(uuid)
        if not client_config:
            logger.warning('Could not fetch endpoint %s on %s, unknown uuid', user_id, uuid)
            return

        client = CtidClient(**client_config)
        logger.debug('user fetcher: scheduling a client.users.get with %s for user %s on %s',
                     client_config, user_id, uuid)
        self.async_runner.run_with_cb(self._on_result, client.users.get, user_id)

    def _on_result(self, result):
        key = result['origin_uuid'], result['id']
        status = result['presence']

        self.forwarder.on_user_status_update(key, status)


def _new_agent_notifier(cti_group_factory, fetcher):
    msg_factory = CTIMessageFormatter.agent_status_update
    return _StatusNotifier(cti_group_factory, msg_factory, fetcher, 'agent')


def _new_endpoint_notifier(cti_group_factory, fetcher):
    msg_factory = CTIMessageFormatter.endpoint_status_update
    return _StatusNotifier(cti_group_factory, msg_factory, fetcher, 'endpoint')


def _new_user_notifier(cti_group_factory, fetcher):
    msg_factory = CTIMessageFormatter.user_status_update
    return _StatusNotifier(cti_group_factory, msg_factory, fetcher, 'user')
