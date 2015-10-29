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

import logging

from collections import defaultdict
from consul import Consul

logger = logging.getLogger(__name__)


class RemoteService(object):

    def __init__(self, service_name, service_id, host, port, tags):
        self._name = service_name
        self._id = service_id
        self._host = host
        self._port = port
        self._tags = tags

    def has_id(self, id_):
        return id_ == self._id

    def to_dict(self):
        return {'host': self._host,
                'port': self._port}

    def __eq__(self, other):
        return (self._name == other._name
                and self._id == other._id
                and self._host == other._host
                and self._port == other._port
                and self._tags == other._tags)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        s = '{class_name}({name}, {id}, {host}, {port}, {tags})'
        return s.format(class_name=self.__class__.__name__,
                        name=self._name,
                        id=self._id,
                        host=self._host,
                        port=self._port,
                        tags=self._tags)

    def __str__(self):
        s = '{name} on {host}:{port}'
        return s.format(name=self._name,
                        host=self._host,
                        port=self._port)

    @classmethod
    def from_bus_msg(cls, msg):
        data = msg['data']
        return cls(data['service_name'],
                   data['service_id'],
                   data['address'],
                   data['port'],
                   data['tags'])

    @classmethod
    def from_consul_service(cls, consul_service):
        return cls(consul_service['ServiceName'],
                   consul_service['ServiceID'],
                   consul_service['ServiceAddress'],
                   consul_service['ServicePort'],
                   consul_service['ServiceTags'])


class RemoteServiceTracker(object):

    def __init__(self, consul_host, consul_port, consul_token):
        self._consul_host = consul_host
        self._consul_port = consul_port
        self._consul_token = consul_token
        self._services = defaultdict(lambda: defaultdict(set))

    def add_service_node(self, service_name, uuid, service):
        logger.debug('adding service %s %s', service, uuid)
        self._services[service_name][uuid].add(service)

    def remove_service_node(self, service_name, service_id, uuid):
        logger.debug('removing service %s %s', service_name, uuid)
        for service in set(self._services[service_name][uuid]):
            if service.has_id(service_id):
                self._services[service_name][uuid].remove(service)

    def fetch_services(self, service_name, uuid):
        logger.debug('fetching %s %s from consul', service_name, uuid)
        client = self._consul_client()
        returned_ids = set()
        for dc in client.catalog.datacenters():
            _, services = client.catalog.service(service_name, dc=dc)
            for service in services:
                service_id = service['ServiceID']
                if uuid in service['ServiceTags'] and service_id not in returned_ids:
                    returned_ids.add(service_id)
                    yield RemoteService.from_consul_service(service)

    def list_services_with_uuid(self, service_name, uuid):
        logger.debug('looking for service "%s" on %s', service_name, uuid)
        if uuid not in self._services.get(service_name, {}):
            for s in self.fetch_services(service_name, uuid):
                self.add_service_node(service_name, uuid, s)

        return self._services[service_name][uuid]

    def _consul_client(self):
        return Consul(self._consul_host, self._consul_port, self._consul_token)
