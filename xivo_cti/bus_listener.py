# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

import json
import logging

from collections import namedtuple
from functools import wraps
from kombu import Queue
from kombu.mixins import ConsumerMixin

Callback = namedtuple('Callback', ['queue', 'callable'])

logger = logging.getLogger(__name__)


def loads_and_ack(f):
    @wraps(f)
    def wrapped(one_self, body, message):
        f(one_self, json.loads(body))
        message.ack()
    return wrapped


def bus_listener_thread(f):
    """
    The decorated function is executed in the bus listener's thread. This means
    that the implementation of the function should only manipulate it's
    parameters and call thread safe operations. Usually add a task to a task
    queue.

    The implementation of this decorator does nothing. It's just a warning for
    the next programmer reading the decorated function.
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapped


class BusListener(ConsumerMixin):

    def __init__(self, connection, exchange):
        self.connection = connection
        self.exchange = exchange
        self._callbacks = []

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=cb.queue, callbacks=[cb.callable]) for cb in self._callbacks]

    def _make_queue(self, routing_key):
        return Queue(exchange=self.exchange, routing_key=routing_key, exclusive=True)

    def add_callback(self, routing_key, callback):
        logger.debug('add_callback: %s %s', routing_key, callback)
        queue = self._make_queue(routing_key)
        cb = Callback(queue, callback)
        self._callbacks.append(cb)
