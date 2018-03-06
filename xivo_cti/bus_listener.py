# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from collections import namedtuple
from functools import wraps
from kombu import Queue
from kombu.mixins import ConsumerMixin

Callback = namedtuple('Callback', ['queue', 'callable'])

logger = logging.getLogger(__name__)


def ack_bus_message(f):
    @wraps(f)
    def wrapped(one_self, body, message):
        f(one_self, body)
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
    return f


class BusListener(ConsumerMixin):

    def __init__(self, connection, exchange):
        self.connection = connection
        self.exchange = exchange
        self._callbacks = []
        self._started = False

    def run(self, *args, **kwargs):
        self._started = True
        super(BusListener, self).run(*args, **kwargs)

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=cb.queue, callbacks=[cb.callable]) for cb in self._callbacks]

    def _make_queue(self, routing_key):
        return Queue(exchange=self.exchange, routing_key=routing_key, exclusive=True)

    def add_callback(self, routing_key, callback):
        if self._started:
            raise RuntimeError('failed to add a new callback: listener already running')
        logger.debug('add_callback: %s %s', routing_key, callback)
        queue = self._make_queue(routing_key)
        cb = Callback(queue, callback)
        self._callbacks.append(cb)
