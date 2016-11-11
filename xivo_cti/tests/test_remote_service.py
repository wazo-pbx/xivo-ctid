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

import unittest

from hamcrest import assert_that, contains, empty, equal_to
from mock import Mock, patch, sentinel as s

from .. import remote_service


class TestRemoteService(unittest.TestCase):

    def test_that_remote_service_is_hashable(self):
        service = remote_service.RemoteService('name', 'id', 'host', 1234, ['abc', 123])

        tuple([service])

    def test_to_dict(self):
        service = remote_service.RemoteService('name', 'id', 'host', 1234, ['abc', 123])

        config = service.to_dict()

        assert_that(config, equal_to({'host': 'host',
                                      'port': 1234}))

    def test_has_id(self):
        service = remote_service.RemoteService('name', 'id', 'host', 1234, ['abc', 123])

        assert_that(service.has_id('id'), equal_to(True))
        assert_that(service.has_id('other'), equal_to(False))

    def test_from_bus_msg(self):
        msg = {'origin_uuid': 'a-uuid',
               'data': {'service_name': 'the-name',
                        'service_id': 'the-id',
                        'address': 'the-address',
                        'port': 'the-port',
                        'tags': ['the', 'tags']}}

        service = remote_service.RemoteService.from_bus_msg(msg)

        expected = remote_service.RemoteService('the-name', 'the-id',
                                                'the-address', 'the-port', ['the', 'tags'])

        assert_that(service, equal_to(expected))

    def test_from_consul_service(self):
        consul_service = {u'Node': u'some_consul_host',
                          u'Service': u'xivo-ctid',
                          u'Port': 9495,
                          u'ID': s.service_id,
                          u'Address': s.service_addr,
                          u'Tags': [u'tag_1', u'tag_2']}

        service = remote_service.RemoteService.from_consul_service(consul_service)

        expected = remote_service.RemoteService(u'xivo-ctid',
                                                s.service_id,
                                                s.service_addr,
                                                9495,
                                                [u'tag_1', u'tag_2'])

        assert_that(service, equal_to(expected))


class TestRemoteServiceTracker(unittest.TestCase):

    def setUp(self):
        self.uuid = 'e4d147b6-f747-4b64-955d-8c36fbcd1d3f'
        consul_conf = {'scheme': s.consul_scheme,
                       'host': s.consul_host,
                       'port': s.consul_port,
                       'token': s.consul_token,
                       'verify': s.consul_verify}
        self.tracker = remote_service.RemoteServiceTracker(
            consul_conf, 'local-uuid', 6666)
        self.finder = self.tracker._finder = Mock(remote_service.Finder)

        self.foobar_service = remote_service.RemoteService('foobar',
                                                           s.service_id,
                                                           s.foobar_host,
                                                           s.foobar_port,
                                                           [s.tag_1])

    def test_that_the_remote_service_tracker_knows_about_itself(self):
        services = self.tracker.list_services_with_uuid('xivo-ctid', 'local-uuid')

        assert_that(services[0].to_dict(), equal_to({'host': 'localhost',
                                                     'port': 6666}))

    def test_fetch_services_will_query_its_finder(self):
        s1, _ = self.finder.list_healthy_services.return_value = [
            {'Service': s.service_name,
             'Tags': [self.uuid],
             'ID': s.service_id,
             'Address': s.service_address,
             'Port': s.service_port},
            {'Tags': ['other-uuid']},
        ]

        services = self.tracker.fetch_services(s.service_name, self.uuid)

        assert_that(services, contains(remote_service.RemoteService.from_consul_service(s1)))

    def test_fetch_errors_during_fetch_services(self):
        self.finder.list_healthy_services.side_effect = remote_service.ServiceDiscoveryError

        services = self.tracker.fetch_services(s.service_name, self.uuid)

        assert_that(list(services), empty())

    def test_that_list_services_will_fetch_from_consul_if_the_service_is_unknown(self):
        with patch.object(self.tracker, 'fetch_services', Mock(return_value=[self.foobar_service])) as fetch:
            services = self.tracker.list_services_with_uuid('foobar', self.uuid)
            fetch.assert_called_once_with('foobar', self.uuid)

        assert_that(services, contains(self.foobar_service))

    def test_that_list_services_returns_known_services_without_fetching_from_consul(self):
        self.tracker.add_service_node('foobar', self.uuid, self.foobar_service)

        with patch.object(self.tracker, 'fetch_services') as fetch:
            services = self.tracker.list_services_with_uuid('foobar', self.uuid)
            assert_that(fetch.call_count, equal_to(0))

        assert_that(services, contains(self.foobar_service))

    def test_add_service_node(self):
        self.tracker.add_service_node('foobar', self.uuid, self.foobar_service)

        services = self.tracker.list_services_with_uuid('foobar', self.uuid)

        assert_that(services, contains(self.foobar_service))

    def test_remove_service_node_does_not_throw(self):
        self.tracker.remove_service_node('foobar', s.service_id, self.uuid)

    def test_that_remove_service_node_removes_the_service(self):
        self.tracker.add_service_node('foobar', self.uuid, self.foobar_service)

        self.tracker.remove_service_node('foobar', s.service_id, self.uuid)

        services = self.tracker.list_services_with_uuid('foobar', self.uuid)
        assert_that(services, empty())
