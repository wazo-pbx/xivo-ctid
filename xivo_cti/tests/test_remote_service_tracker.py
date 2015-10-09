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

import unittest

from hamcrest import assert_that, contains, empty
from mock import Mock, patch, sentinel as s

from .. import remote_service_tracker


class TestRemoteServiceTracker(unittest.TestCase):

    def setUp(self):
        self.uuid = 'e4d147b6-f747-4b64-955d-8c36fbcd1d3f'
        self.tracker = remote_service_tracker.RemoteServiceTracker(s.consul_host,
                                                                   s.consul_port,
                                                                   s.consul_token)

    @patch('xivo_cti.remote_service_tracker.Consul')
    def test_that_list_nodes_returns_available_services(self, Consul):
        consul_client = Consul.return_value
        consul_client.catalog.service.return_value = ('index', [])

        configs = self.tracker.list_nodes_with_uuid('foobar', self.uuid)

        assert_that(configs, empty())
        consul_client.catalog.service.assert_called_once_with('foobar', tags=self.uuid)

    @patch('xivo_cti.remote_service_tracker.Consul')
    def test_consul_is_not_called_every_time(self, Consul):
        consul_client = Consul.return_value
        consul_client.catalog.service.return_value = ('273024', [{u'Node': u'pcm-dev-2',
                                                                  u'ServiceName': u'xivo-ctid',
                                                                  u'ServicePort': 9495,
                                                                  u'ServiceID': s.service_id,
                                                                  u'ServiceAddress': u'10.37.2.254',
                                                                  u'Address': u'127.0.0.1',
                                                                  u'ServiceTags': [u'Québec', 'xivo-ctid', self.uuid]}])

        configs_1 = self.tracker.list_nodes_with_uuid('foobar', self.uuid)
        configs_2 = self.tracker.list_nodes_with_uuid('foobar', self.uuid)
        configs_3 = self.tracker.list_nodes_with_uuid('foobar', self.uuid)

        consul_client.catalog.service.assert_called_once_with('foobar', tags=self.uuid)
        assert_that(configs_1, contains({'name': 'xivo-ctid',
                                         'address': '10.37.2.254',
                                         'port': 9495,
                                         'tags': [u'Québec', 'xivo-ctid', self.uuid],
                                         'id': s.service_id}))
        assert_that(configs_1 == configs_2 == configs_3)

    @patch('xivo_cti.remote_service_tracker.Consul')
    def test_that_list_nodes_returns_available_services_with_results(self, Consul):
        consul_client = Consul.return_value
        consul_client.catalog.service.return_value = ('273024', [{u'Node': u'pcm-dev-2',
                                                                  u'ServiceName': u'xivo-ctid',
                                                                  u'ServicePort': 9495,
                                                                  u'ServiceID': s.service_id,
                                                                  u'ServiceAddress': u'10.37.2.254',
                                                                  u'Address': u'127.0.0.1',
                                                                  u'ServiceTags': [u'Québec', 'xivo-ctid', self.uuid]}])

        configs = self.tracker.list_nodes_with_uuid('foobar', self.uuid)

        assert_that(configs, contains({'name': 'xivo-ctid',
                                       'address': '10.37.2.254',
                                       'port': 9495,
                                       'tags': [u'Québec', 'xivo-ctid', self.uuid],
                                       'id': s.service_id}))

    def test_add_service_node(self):
        self.tracker.add_service_node('foobar', s.service_id, self.uuid, s.foobar_host, s.foobar_port, s.foobar_tags)

        configs = self.tracker.list_nodes_with_uuid('foobar', self.uuid)

        assert_that(configs, contains({'name': 'foobar',
                                       'address': s.foobar_host,
                                       'port': s.foobar_port,
                                       'tags': s.foobar_tags,
                                       'id': s.service_id}))

    def test_remove_service_node_does_not_throw(self):
        self.tracker.remove_service_node('foobar', s.service_id, self.uuid)

    @patch('xivo_cti.remote_service_tracker.Consul', Mock())
    def test_that_remove_service_node_removes_the_service(self):
        self.tracker.add_service_node('foobar', s.service_id, self.uuid, s.foobar_host, s.foobar_port, s.foobar_tags)

        self.tracker.remove_service_node('foobar', s.service_id, self.uuid)

        configs = self.tracker.list_nodes_with_uuid('foobar', self.uuid)

        assert_that(configs, empty())
