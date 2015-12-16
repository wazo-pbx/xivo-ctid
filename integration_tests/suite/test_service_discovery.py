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
import time
import socket

from docker import Client
from consul import Consul
from hamcrest import assert_that, equal_to, not_

from .base import BaseCTIDIntegrationTests


class TestServiceDiscovery(BaseCTIDIntegrationTests):

    asset = 'service_discovery'

    @classmethod
    def setUpClass(cls):
        super(TestServiceDiscovery, cls).setUpClass()
        cls.stop_service('cti2')

    def test_that_service_is_registered_on_consul_on_start(self):
        registered = self._is_ctid_registered_to_consul()

        assert_that(registered, 'xivo-ctid should be registered on consul')

        self.stop_service('ctid')

        registered = self._is_ctid_registered_to_consul()

        assert_that(not_(registered), 'xivo-ctid should not be registered on consul')

    def test_that_remote_service_discovery_works_when_remote_started_after(self):
        self.start_service('cti2')
        time.sleep(1)
        uuid = 'foobar'

        status = self._get_endpoint_status(uuid, 42)

        assert_that(status, equal_to('patate'))

    def _find_host(self, container_name):
        c = Client(base_url='unix://var/run/docker.sock')
        long_name = u'/{asset}_{name}_1'.format(asset=self.asset.replace('_', ''), name=container_name)
        print long_name
        for container in c.containers():
            if long_name in container['Names']:
                return c.inspect_container(container['Id'])['NetworkSettings']['IPAddress']
        raise LookupError('could not find a running %s', container_name)

    def _get_endpoint_status(self, uuid, endpoint_id):
        ctid_host = self._find_host('ctid')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        start = time.time()
        while True:
            try:
                sock.connect((ctid_host, 5005))
                break
            except socket.error:
                if time.time() - start > 5:
                    assert False
                time.sleep(0.25)
        sock.send('register endpoint {} {}'.format(uuid, endpoint_id))
        start = time.time()
        while True:
            buf = sock.recv(4096)
            if buf.strip() == 'XIVO-INFO:KO':
                return None
            elif buf.strip() == 'XIVO-INFO:OK':
                continue
            else:
                return json.loads(buf)['data']['status']
            if time.time() - start > 5:
                raise LookupError('could not get endpoint status')
            time.sleep(0.25)

    def _is_ctid_registered_to_consul(self):
        consul = Consul('localhost', '8500', 'the_one_ring')

        start = time.time()
        while time.time() - start < 10:
            services = consul.agent.services()
            for index, service in services.iteritems():
                if service['Service'] == 'xivo-ctid' and service['Address'] == 'ctid':
                    return True
            time.sleep(1)

        return False
