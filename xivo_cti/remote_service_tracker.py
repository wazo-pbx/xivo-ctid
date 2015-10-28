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


class RemoteServiceTracker(object):

    def __init__(self, consul_host, consul_port, consul_token):
        self._consul_host = consul_host
        self._consul_port = consul_port
        self._consul_token = consul_token
        self._services = defaultdict(lambda: defaultdict(set))

    def add_service_node(self, service_name, service_id, uuid, host, port, tags):
        new_config = {'name': service_name,
                      'address': host,
                      'port': port,
                      'tags': tags,
                      'id': service_id}
        self._services[service_name][uuid].append(new_config)

    def remove_service_node(self, service_name, service_id, uuid):
        for config in self._services[service_name][uuid]:
            if config['id'] == service_id:
                self._services[service_name][uuid].remove(config)

    def list_nodes_with_uuid(self, service_name, uuid):
        logger.debug('looking for service "%s" on %s', service_name, uuid)
        if uuid not in self._services.get(service_name, {}):
            client = self._consul_client()
            data_centers = client.catalog.datacenters()
            for dc in data_centers:
                _, services = client.catalog.service(service_name, tags=uuid, dc=dc)
                for service in services:
                    self._services[service_name][uuid].add(self._service_info(service))

        return list(self._services[service_name][uuid])

    def _consul_client(self):
        return Consul(self._consul_host, self._consul_port, self._consul_token)

    @staticmethod
    def _service_info(consul_service):
        return {'name': consul_service['ServiceName'],
                'address': consul_service['ServiceAddress'],
                'port': consul_service['ServicePort'],
                'tags': consul_service['ServiceTags'],
                'id': consul_service['ServiceID']}
