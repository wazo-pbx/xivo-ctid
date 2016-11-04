# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
# Copyright (C) 2016 Proformatique, Inc.
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

import requests

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

    def __init__(self, consul_config, local_uuid, http_port, service_discovery_config):
        this_xivo_ctid = RemoteService('xivo-ctid', None, 'localhost', http_port, ['xivo-ctid', local_uuid])
        self._services = defaultdict(lambda: defaultdict(set))
        self._services_lock = threading.Lock()
        self.add_service_node('xivo-ctid', local_uuid, this_xivo_ctid)
        self._finder = Finder(consul_config, service_discovery_config.get('tokens', {}))

    def add_service_node(self, service_name, uuid, service):
        logger.info('adding service %s %s', service, uuid)
        with self._services_lock:
            self._services[service_name][uuid].add(service)

    def remove_service_node(self, service_name, service_id, uuid):
        logger.debug('removing service %s %s', service_name, uuid)
        for service in set(self._services[service_name][uuid]):
            if service.has_id(service_id):
                with self._services_lock:
                    self._services[service_name][uuid].remove(service)

    def fetch_services(self, service_name, uuid):
        logger.debug('fetching %s %s from consul', service_name, uuid)
        for service in self._finder.list_healthy_services(service_name):
            if uuid not in service['ServiceTags']:
                continue
            yield RemoteService.from_consul_service(service)

    def list_services_with_uuid(self, service_name, uuid):
        logger.debug('looking for service "%s" on %s', service_name, uuid)
        if uuid not in self._services.get(service_name, {}):
            for s in self.fetch_services(service_name, uuid):
                self.add_service_node(service_name, uuid, s)

        with self._services_lock:
            return list(self._services[service_name][uuid])


class ServiceDiscoveryError(Exception):
    pass


class Finder(object):

    def __init__(self, consul_config, remote_tokens):
        self._dc_url = '{scheme}://{host}:{port}/v1/catalog/datacenters'.format(**consul_config)
        self._health_url = '{scheme}://{host}:{port}/v1/health/service'.format(**consul_config)
        self._service_url = '{scheme}://{host}:{port}/v1/catalog/service'.format(**consul_config)
        self._verify = consul_config.get('verify', True)
        self._tokens = remote_tokens
        self._local_token = consul_config.get('token')

    def list_healthy_services(self, service_name):
        services = []
        for dc in self._get_datacenters():
            healthy = self._get_healthy(service_name, dc)
            for service in self._list_services(service_name, dc):
                if service.get('ServiceID') not in healthy:
                    continue
                services.append(service)
        return services

    def _filter_health_services(self, service_name, query_result):
        ids = set()
        for node in query_result:
            for check in node.get('Checks', []):
                service_id = check.get('ServiceID')
                if not service_id:
                    continue
                if service_name != check.get('ServiceName'):
                    continue
                ids.add(service_id)
        return list(ids)

    def _get_datacenters(self):
        response = requests.get(self._dc_url,
                                verify=self._verify)
        self._assert_ok(response)
        return response.json()

    def _get_healthy(self, service_name, datacenter):
        headers = {'X-Consul-Token': self._get_token(datacenter)}
        url = '{}/{}'.format(self._health_url, service_name)
        response = requests.get(url,
                                verify=self._verify,
                                params={'dc': datacenter, 'passing': True},
                                headers=headers)
        self._assert_ok(response)
        return self._filter_health_services(service_name, response.json())

    def _get_token(self, datacenter):
        return self._tokens.get(datacenter, self._local_token)

    def _list_services(self, service_name, datacenter):
        headers = {'X-Consul-Token': self._get_token(datacenter)}
        url = '{}/{}'.format(self._service_url, service_name)
        response = requests.get(url, verify=self._verify, params={'dc': datacenter}, headers=headers)
        self._assert_ok(response)
        return response.json()

    @staticmethod
    def _assert_ok(response, code=200):
        if response.status_code != code:
            msg = getattr(response, 'text', 'unknown error')
            raise ServiceDiscoveryError(msg)
