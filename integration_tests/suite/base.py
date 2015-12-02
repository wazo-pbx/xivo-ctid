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

from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase

DB_USER = 'asterisk'
DB_PASSWORD = 'proformatique'
DB_HOST = 'localhost'
DB_PORT = '15432'
DB_NAME = 'asterisk'
DB_URL = ('postgresql://{user}:{password}@{host}:{port}/{db_name}'
          .format(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, db_name=DB_NAME))


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
        for _ in countdown(20):
            try:
                conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
                cur = conn.cursor()
                cur.execute('SELECT count(*) FROM userfeatures')
                conn.close()
                break
            except psycopg2.OperationalError:
                print '.',
                time.sleep(1)
        print 'PG is started'

    @classmethod
    def wait_for(cls, service):
        for _ in countdown(5):
            cls._run_cmd('docker-compose start {}'.format(service))
            if cls.service_status(service)['State']['Running']:
                return
            time.sleep(1)

    @classmethod
    def stop_service(cls, service):
        cls._run_cmd('docker-compose stop {}'.format(service))
        for _ in countdown(5):
            try:
                if not cls.service_status(service)['State']['Running']:
                    return
            except ValueError:
                pass
            time.sleep(1)

    def start_service(self, service):
        self.wait_for(service)


def countdown(n):
    while n > 0:
        yield n
        n = n - 1
    raise Exception('countdown reached 0')
