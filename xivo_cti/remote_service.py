# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# Copyright (C) 2016 Proformatique, Inc.
# SPDX-License-Identifier: GPL-3.0+

import logging
import threading
from collections import defaultdict

from xivo.consul_helpers import ServiceFinder as Finder, ServiceDiscoveryError

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
        return (self._name == other._name and
                self._id == other._id and
                self._host == other._host and
                self._port == other._port and
                self._tags == other._tags)

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
        return cls(consul_service['Service'],
                   consul_service['ID'],
                   consul_service['Address'],
                   consul_service['Port'],
                   consul_service['Tags'])


class RemoteServiceTracker(object):

    def __init__(self, consul_config, local_uuid, http_port):
        this_xivo_ctid = RemoteService('xivo-ctid', None, 'localhost', http_port, ['xivo-ctid', local_uuid])
        self._services = defaultdict(lambda: defaultdict(set))
        self._services_lock = threading.Lock()
        self.add_service_node('xivo-ctid', local_uuid, this_xivo_ctid)
        self._finder = Finder(consul_config)

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
        try:
            for service in self._finder.list_healthy_services(service_name):
                if uuid not in service['Tags']:
                    continue
                yield RemoteService.from_consul_service(service)
        except ServiceDiscoveryError as e:
            logger.info('failed to find %s %s: %s', service_name, uuid, str(e))

    def list_services_with_uuid(self, service_name, uuid):
        logger.debug('looking for service "%s" on %s', service_name, uuid)
        if uuid not in self._services.get(service_name, {}):
            for s in self.fetch_services(service_name, uuid):
                self.add_service_node(service_name, uuid, s)

        with self._services_lock:
            return list(self._services[service_name][uuid])
