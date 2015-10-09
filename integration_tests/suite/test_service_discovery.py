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

import os
import time
import psycopg2

from consul import Consul
from hamcrest import assert_that, not_
from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase


class BaseCTIDIntegrationTests(AssetLaunchingTestCase):

    service = 'ctid'
    assets_root = os.path.join(os.path.dirname(__file__), '..', 'assets')

    @classmethod
    def setUpClass(cls):
        cls.launch_service_with_asset()
        cls.wait_for_pg()
        cls.wait_for('agentd')
        cls.wait_for('ctid')

    @classmethod
    def wait_for_pg(cls):
        for _ in countdown(120):
            try:
                conn = psycopg2.connect(host='localhost', port=15432, user='asterisk', password='proformatique', database='asterisk')
                cur = conn.cursor()
                cur.execute('SELECT count(*) FROM userfeatures')
                conn.close()
                break
            except psycopg2.OperationalError:
                time.sleep(1)

    @classmethod
    def wait_for(cls, service):
        for _ in countdown(5):
            cls._run_cmd('docker-compose start {}'.format(service))
            running = cls.service_status(service)[0]['State']['Running']
            if running:
                return
            time.sleep(1)

    def stop_service(self, service):
        self._run_cmd('docker-compose stop {}'.format(service))
        for _ in countdown(5):
            running = self.service_status(service)[0]['State']['Running']
            if not running:
                return
            time.sleep(1)


def countdown(n):
    while n > 0:
        yield n
        n = n - 1
    raise Exception('countdown reached 0')


class TestServiceDiscovery(BaseCTIDIntegrationTests):

    asset = 'service_discovery'

    def test_that_service_is_registered_on_consul_on_start(self):
        registered = self._is_ctid_registered_to_consul()

        assert_that(registered, 'xivo-ctid should be registered on consul')

        self.stop_service('ctid')

        registered = self._is_ctid_registered_to_consul()

        assert_that(not_(registered), 'xivo-ctid should not be registered on consul')

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
