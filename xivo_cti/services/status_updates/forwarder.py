# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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
import threading

from collections import defaultdict
from xivo_bus.ctl.config import BusConfig
from xivo_bus.ctl.consumer import BusConsumer
from xivo_cti import config
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter

logger = logging.getLogger(__name__)


class ThreadedStatusListener(object):

    def __init__(self, config, task_queue, forwarder):
        self._thread = threading.Thread(target=StatusListener, args=(config, task_queue, forwarder))
        self._thread.start()


class StatusListener(object):

    def __init__(self, config, task_queue, forwarder):
        notifier_config = dict(config['status_notifier'])
        routing_keys = notifier_config.pop('routing_keys')
        queue_name = 'xivo-status-updates'
        bus_config = BusConfig(
            queue_name=queue_name,
            **notifier_config
        )
        self._forwarder = forwarder
        self._task_queue = task_queue
        self._consumer = BusConsumer(bus_config)
        self._consumer.connect()

        self._consumer.add_binding(
            self.queue_endpoint_status_update,
            queue_name,
            notifier_config['exchange_name'],
            routing_keys['endpoint'],
        )
        self._consumer.add_binding(
            self.queue_user_status_update,
            queue_name,
            notifier_config['exchange_name'],
            routing_keys['user'],
        )

        self._consumer.run()

    def __delete__(self):
        self._consumer.stop()

    def queue_endpoint_status_update(self, event):
        self._task_queue.put(self._forwarder.on_endpoint_status_update, event)

    def queue_user_status_update(self, event):
        self._task_queue.put(self._forwarder.on_user_status_update, event)


class StatusForwarder(object):

    _id_field_map = {
        'endpoint_status_update': 'endpoint_id',
        'user_status_update': 'user_id',
    }

    def __init__(self,
                 cti_group_factory,
                 task_queue,
                 endpoint_status=None,
                 user_status_notifier=None):
        logger.debug('StatusForwarder instantiation')
        self._task_queue = task_queue
        self.endpoint_status_notifier = endpoint_status or _new_endpoint_notifier(cti_group_factory)
        self._user_status_notifier = user_status_notifier or _new_user_notifier(cti_group_factory)

    def run(self):
        self._listener = ThreadedStatusListener(config, self._task_queue, self)

    def on_endpoint_status_update(self, event):
        logger.debug('New endpoint status event: %s', event)
        key = self._extract_key(event)
        new_status = event['data']['status']

        self.endpoint_status_notifier.update(key, new_status)

    def on_user_status_update(self, event):
        logger.debug('New user status event: %s', event)
        key = self._extract_key(event)
        new_status = event['data']['status']

        self._user_status_notifier.update(key, new_status)

    def _extract_key(self, event):
        id_field = self._id_field_map[event['name']]
        return event['data']['xivo_id'], event['data'][id_field]


class StatusNotifier(object):

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


def _new_endpoint_notifier(cti_group_factory):
    msg_factory = CTIMessageFormatter.endpoint_status_update
    return StatusNotifier(cti_group_factory, msg_factory)


def _new_user_notifier(cti_group_factory):
    msg_factory = CTIMessageFormatter.user_status_update
    return StatusNotifier(cti_group_factory, msg_factory)
