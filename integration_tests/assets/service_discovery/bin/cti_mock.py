#!/usr/bin/env python
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

import contextlib
import time
import socket
from threading import Timer

from kombu import Connection, Exchange, Producer
from flask import Flask, jsonify

from xivo.consul_helpers import NotifyingRegisterer
from xivo_bus import Marshaler, Publisher

UUID = 'foobar'

app = Flask('xivo-ctid mock')


@contextlib.contextmanager
def consul_registration():
    bus_url = 'amqp://{username}:{password}@{host}:{port}//'.format(username='guest',
                                                                    password='guest',
                                                                    host='rabbitmq',
                                                                    port=5672)
    bus_connection = Connection(bus_url)
    bus_exchange = Exchange('xivo', type='topic')
    bus_producer = Producer(bus_connection, exchange=bus_exchange, auto_declare=True)
    bus_marshaler = Marshaler(UUID)
    bus_publisher = Publisher(bus_producer, bus_marshaler)
    config = {'consul': {'host': 'consul',
                         'port': 8500,
                         'token': 'the_one_ring',
                         'advertise_address': 'cti2',
                         'advertise_port': 6262,
                         'check_url': 'http://cti2:6262/0.1/infos',
                         'check_url_timeout': '3s',
                         'check_url_interval': '30s'},
              'uuid': UUID}
    registerer = NotifyingRegisterer.from_config('xivo-ctid', bus_publisher, config)
    registerer.register()
    t = Timer(0.5, registerer.register)
    t.start()
    try:
        yield
    finally:
        registerer.deregister()


@app.route('/0.1/infos')
def infos():
    return jsonify({'uuid': UUID})


@app.route('/0.1/endpoints/<int:endpoint_id>')
def endpoints(endpoint_id):
    status = 'patate'
    return jsonify({'id': endpoint_id,
                    'origin_uuid': UUID,
                    'status': status})


@app.route('/0.1/users/<int:user_id>')
def users(user_id):
    presence = 'poil'
    return jsonify({'id': user_id,
                    'origin_uuid': UUID,
                    'presence': presence})


def main():
    start_time = time.time()
    while True:
        try:
            with consul_registration():
                app.run(host="0.0.0.0", port=6262, debug=True)
            return
        except socket.error:
            if start_time - time.time() > 10:
                print 'Failed to connect to rabbitmq'
                return
            time.sleep(0.25)


if __name__ == '__main__':
    main()
