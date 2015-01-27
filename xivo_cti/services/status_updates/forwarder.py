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

from functools import wraps
from kombu.mixins import ConsumerMixin
from kombu import Exchange, Queue
from kombu import Connection

from collections import defaultdict
from xivo_cti import config
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter

logger = logging.getLogger(__name__)


class StatusForwarder(object):

    _id_field_map = {
        'agent_status_update': 'agent_id',
        'endpoint_status_update': 'endpoint_id',
        'user_status_update': 'user_id',
    }

    def __init__(self,
                 cti_group_factory,
                 task_queue,
                 _agent_status_notifier=None,
                 _endpoint_status_notifier=None,
                 _user_status_notifier=None):
        logger.debug('StatusForwarder instantiation')
        self._task_queue = task_queue
        self.agent_status_notifier = _agent_status_notifier or _new_agent_notifier(cti_group_factory)
        self.endpoint_status_notifier = _endpoint_status_notifier or _new_endpoint_notifier(cti_group_factory)
        self.user_status_notifier = _user_status_notifier or _new_user_notifier(cti_group_factory)

    def run(self):
        self._listener = _ThreadedStatusListener(config, self._task_queue, self)

    def on_agent_status_update(self, event):
        logger.debug('New agent status event: %s', event)
        key = self._extract_key(event)
        new_status = event['data']['status']

        self.agent_status_notifier.update(key, new_status)

    def on_endpoint_status_update(self, event):
        logger.debug('New endpoint status event: %s', event)
        key = self._extract_key(event)
        new_status = event['data']['status']

        self.endpoint_status_notifier.update(key, new_status)

    def on_user_status_update(self, event):
        logger.debug('New user status event: %s', event)
        key = self._extract_key(event)
        new_status = event['data']['status']

        self.user_status_notifier.update(key, new_status)

    def _extract_key(self, event):
        id_field = self._id_field_map[event['name']]
        return event['data']['xivo_id'], event['data'][id_field]


class _ThreadedStatusListener(object):

    def __init__(self, config, task_queue, forwarder):
        self._thread = threading.Thread(target=_StatusListener, args=(config, task_queue, forwarder))
        self._thread.start()


def _loads_and_ack(f):
    @wraps(f)
    def wrapped(one_self, body, message):
        f(one_self, json.loads(body))
        message.ack()
    return wrapped


class _StatusWorker(ConsumerMixin):

    def __init__(self, connection, exchange, task_queue, forwarder, routing_keys):
        self.connection = connection
        self.exchange = exchange
        self._task_queue = task_queue
        self._forwarder = forwarder
        self._agent_queue = self._make_queue(routing_keys['agent_status'])
        self._user_queue = self._make_queue(routing_keys['user_status'])
        self._endpoint_queue = self._make_queue(routing_keys['endpoint_status'])

    def _make_queue(self, routing_key):
        return Queue(exchange=self.exchange, routing_key=routing_key, exclusive=True, auto_delete=True)

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=self._agent_queue,
                         callbacks=[self._on_agent_status]),
                Consumer(queues=self._user_queue,
                         callbacks=[self._on_user_status]),
                Consumer(queues=self._endpoint_queue,
                         callbacks=[self._on_endpoint_status])]

    @_loads_and_ack
    def _on_agent_status(self, body):
        self._task_queue.put(self._forwarder.on_agent_status_update, body)

    @_loads_and_ack
    def _on_user_status(self, body):
        self._task_queue.put(self._forwarder.on_user_status_update, body)

    @_loads_and_ack
    def _on_endpoint_status(self, body):
        self._task_queue.put(self._forwarder.on_endpoint_status_update, body)


class _StatusListener(object):

    def __init__(self, config, task_queue, forwarder):
        bus_url = 'amqp://{username}:{password}@{host}:{port}//'.format(**config['bus'])
        exchange = Exchange(config['bus']['exchange_name'], type=config['bus']['exchange_type'])
        with Connection(bus_url) as conn:
            _StatusWorker(conn, exchange, task_queue, forwarder, config['bus']['routing_keys']).run()


class _StatusNotifier(object):

    def __init__(self, cti_group_factory, message_factory):
        self._subscriptions = defaultdict(cti_group_factory.new_cti_group)
        self._message_factory = message_factory
        self._statuses = {}

    def register(self, connection, keys):
        for key in keys:
            logger.debug('Registering to %s', key)
            self._subscriptions[key].add(connection)
            status_msg = self._statuses.get(key)
            if status_msg:
                connection.send_message(status_msg)
        logger.debug('Subcriptions: %s', self._subscriptions.keys())

    def unregister(self, connection, keys):
        for key in keys:
            self._subscriptions[key].remove(connection)

    def update(self, key, new_status):
        logger.debug('%s updated %s', key, new_status)
        msg = self._message_factory(key, new_status)
        self._statuses[key] = msg

        subscription = self._subscriptions.get(key)
        if subscription is None:
            logger.debug('No subscriptions for %s in %s', key, self._subscriptions.keys())
            return

        logger.debug('Sending %s', msg)
        subscription.send_message(msg)


def _new_agent_notifier(cti_group_factory):
    msg_factory = CTIMessageFormatter.agent_status_update
    return _StatusNotifier(cti_group_factory, msg_factory)


def _new_endpoint_notifier(cti_group_factory):
    msg_factory = CTIMessageFormatter.endpoint_status_update
    return _StatusNotifier(cti_group_factory, msg_factory)


def _new_user_notifier(cti_group_factory):
    msg_factory = CTIMessageFormatter.user_status_update
    return _StatusNotifier(cti_group_factory, msg_factory)
