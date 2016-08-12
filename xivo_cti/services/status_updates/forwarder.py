# -*- coding: utf-8 -*-

# Copyright (C) 2014-2016 Avencall
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
import xivo_agentd_client

from uuid import UUID

from collections import defaultdict
from contextlib import contextmanager
from requests.exceptions import RequestException

from xivo_ctid_client import Client as CtidClient
from xivo_bus.resources.cti.event import (AgentStatusUpdateEvent,
                                          UserStatusUpdateEvent,
                                          EndpointStatusUpdateEvent)
from xivo_cti import config, dao
from xivo_cti.async_runner import async_runner_thread
from xivo_cti.bus_listener import bus_listener_thread, ack_bus_message
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter
from xivo_cti.exception import NoSuchUserException
from xivo_cti.remote_service import RemoteService

logger = logging.getLogger(__name__)


class StatusForwarder(object):

    _id_field_map = {'agent_status_update': AgentStatusUpdateEvent.id_field,
                     'endpoint_status_update': EndpointStatusUpdateEvent.id_field,
                     'user_status_update': UserStatusUpdateEvent.id_field}

    def __init__(self,
                 xivo_uuid,
                 cti_group_factory,
                 task_queue,
                 bus_listener,
                 async_runner,
                 remote_service_tracker,
                 _agent_status_notifier=None,
                 _endpoint_status_notifier=None,
                 _user_status_notifier=None):
        agent_status_fetcher = _AgentStatusFetcher(self, async_runner, remote_service_tracker, xivo_uuid)
        endpoint_status_fetcher = _EndpointStatusFetcher(self, async_runner, remote_service_tracker, xivo_uuid)
        user_status_fetcher = _UserStatusFetcher(self, async_runner, remote_service_tracker, xivo_uuid)
        self._bus_listener = bus_listener
        self._task_queue = task_queue
        self.agent_status_notifier = _agent_status_notifier or _new_agent_notifier(cti_group_factory, agent_status_fetcher)
        self.endpoint_status_notifier = _endpoint_status_notifier or _new_endpoint_notifier(cti_group_factory, endpoint_status_fetcher)
        self.user_status_notifier = _user_status_notifier or _new_user_notifier(cti_group_factory, user_status_fetcher)
        self._remote_service_tracker = remote_service_tracker

        self._bus_listener.add_callback(AgentStatusUpdateEvent.routing_key, self._on_bus_agent_status)
        self._bus_listener.add_callback(UserStatusUpdateEvent.routing_key, self._on_bus_user_status)
        self._bus_listener.add_callback(EndpointStatusUpdateEvent.routing_key, self._on_bus_endpoint_status)
        self._bus_listener.add_callback('service.registered.#', self._on_bus_service_registered)
        self._bus_listener.add_callback('service.deregistered.#', self._on_bus_service_deregistered)

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

    def _extract_key(self, event):
        id_field = self._id_field_map[event['name']]
        return event['origin_uuid'], event['data'][id_field]

    @bus_listener_thread
    @ack_bus_message
    def _on_bus_service_registered(self, body):
        service = RemoteService.from_bus_msg(body)
        uuid = body['origin_uuid']
        service_name = body['data']['service_name']
        self._task_queue.put(self._remote_service_tracker.add_service_node,
                             service_name, uuid, service)
        self._task_queue.put(self.on_service_added, service_name, uuid)

    @bus_listener_thread
    @ack_bus_message
    def _on_bus_service_deregistered(self, body):
        uuid = body['origin_uuid']
        service_name = body['data']['service_name']
        service_id = body['data']['service_id']
        self._task_queue.put(self._remote_service_tracker.remove_service_node,
                             service_name, service_id, uuid)

    @bus_listener_thread
    @ack_bus_message
    def _on_bus_agent_status(self, body):
        key = self._extract_key(body)
        status = body['data']['status']
        self._task_queue.put(self.on_agent_status_update, key, status)

    @bus_listener_thread
    @ack_bus_message
    def _on_bus_user_status(self, body):
        key = self._extract_key(body)
        status = body['data']['status']
        self._task_queue.put(self.on_user_status_update, key, status)

    @bus_listener_thread
    @ack_bus_message
    def _on_bus_endpoint_status(self, body):
        key = self._extract_key(body)
        status = body['data']['status']
        self._task_queue.put(self.on_endpoint_status_update, key, status)


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
            keys = []
            for uuid, subscriptions in self._subscriptions.iteritems():
                for id_ in subscriptions.iterkeys():
                    keys.append((uuid, id_))
            logger.debug('No subscriptions for %s in %s', key, keys)
            return

        subscription.send_message(msg)


class _UserStatusNotifier(_StatusNotifier):
    # Allow the user registration to work by id or uuid

    def register(self, connection, keys):
        updated_keys = self._update_keys(keys)
        super(_UserStatusNotifier, self).register(connection, updated_keys)

    def unregister(self, connection, keys):
        updated_keys = self._update_keys(keys)
        super(_UserStatusNotifier, self).register(connection, updated_keys)

    def _update_keys(self, keys):
        new_keys = []
        for xivo_uuid, id_or_uuid in keys:
            if self._is_uuid(id_or_uuid):
                return keys

            try:
                user = dao.user.get(str(id_or_uuid))
            except NoSuchUserException:
                continue

            new_keys.append((xivo_uuid, user['uuid']))

        return new_keys

    @staticmethod
    def _is_uuid(id_or_uuid):
        try:
            UUID(id_or_uuid)
            return True
        except (AttributeError, ValueError):
            return False


class _BaseStatusFetcher(object):

    def __init__(self, status_forwarder, async_runner, remote_service_tracker, xivo_uuid):
        self.forwarder = status_forwarder
        self.async_runner = async_runner
        self._remote_service_tracker = remote_service_tracker
        self._uuid = xivo_uuid

    def fetch(self, key):
        uuid, resource_id = key
        if not resource_id:
            return
        self.async_runner.run_with_cb(self._on_result, self._fetch, uuid, resource_id)

    @contextmanager
    def exception_logging_client(self, uuid):
        client = self._client(uuid)
        try:
            yield client
        except RequestException as e:
            logger.warning('status_fetcher: could not fetch status: %s', e)
        except AttributeError:
            if not client:
                logger.warning('status_fetcher: cannot find a running service %s %s', self.service, uuid)
            else:
                raise


class _CtidStatusFetcher(_BaseStatusFetcher):

    service = 'xivo-ctid'

    def _client(self, uuid):
        for service in self._remote_service_tracker.list_services_with_uuid(self.service, uuid):
            return CtidClient(**service.to_dict())


class _AgentStatusFetcher(_BaseStatusFetcher):

    service = 'xivo-agentd'

    def _client(self, uuid):
        if uuid == self._uuid:
            token = config['auth']['token']
            return xivo_agentd_client.Client(token=token, **config['agentd'])

    @async_runner_thread
    def _fetch(self, uuid, agent_id):
        logger.info('agent_status_fetcher: fetching agent %s@%s', agent_id, uuid)
        with self.exception_logging_client(uuid) as client:
            return client.agents.get_agent_status(agent_id)

    def _on_result(self, result):
        if not result:
            return
        key = result.origin_uuid, result.id
        status = 'logged_in' if result.logged else 'logged_out'

        self.forwarder.on_agent_status_update(key, status)


class _EndpointStatusFetcher(_CtidStatusFetcher):

    @async_runner_thread
    def _fetch(self, uuid, endpoint_id):
        logger.info('endpoint_status_fetcher: fetching endpoint %s@%s', endpoint_id, uuid)
        with self.exception_logging_client(uuid) as client:
            return client.endpoints.get(endpoint_id)

    def _on_result(self, result):
        if not result:
            return
        key = result['origin_uuid'], result['id']
        status = result['status']

        self.forwarder.on_endpoint_status_update(key, status)


class _UserStatusFetcher(_CtidStatusFetcher):

    @async_runner_thread
    def _fetch(self, uuid, user_uuid):
        logger.info('user_status_fetcher: fetching user %s@%s', user_uuid, uuid)
        with self.exception_logging_client(uuid) as client:
            return client.users.get(user_uuid)

    def _on_result(self, result):
        if not result:
            return
        key = result['origin_uuid'], result['user_uuid']
        status = result['presence']

        self.forwarder.on_user_status_update(key, status)


def _new_agent_notifier(cti_group_factory, fetcher):
    msg_factory = CTIMessageFormatter.agent_status_update
    return _StatusNotifier(cti_group_factory, msg_factory, fetcher, 'agent')


def _new_endpoint_notifier(cti_group_factory, fetcher):
    msg_factory = CTIMessageFormatter.endpoint_status_update
    return _StatusNotifier(cti_group_factory, msg_factory, fetcher, 'endpoint')


def _new_user_notifier(cti_group_factory, fetcher):
    msg_factory = _UserStatusMessageFactory()
    return _UserStatusNotifier(cti_group_factory, msg_factory, fetcher, 'user')


class _UserStatusMessageFactory(object):

    def __call__(self, key, status):
        xivo_uuid, user_uuid = key
        try:
            user_id = dao.user.get(user_uuid)['id']
        except NoSuchUserException:
            # This case should happen in acceptance tests only
            logger.info('Received a status update from an unknown user: %s', user_uuid)
            user_id = None
        return CTIMessageFormatter.user_status_update(xivo_uuid, user_uuid, user_id, status)

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)
