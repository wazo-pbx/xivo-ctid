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

from hamcrest import assert_that, calling, contains, empty, equal_to, raises
from mock import ANY, Mock, patch, sentinel as s

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
                          u'ServiceName': u'xivo-ctid',
                          u'ServicePort': 9495,
                          u'ServiceID': s.service_id,
                          u'ServiceAddress': s.service_addr,
                          u'Address': u'127.0.0.1',
                          u'ServiceTags': [u'tag_1', u'tag_2']}

        service = remote_service.RemoteService.from_consul_service(consul_service)

        expected = remote_service.RemoteService(u'xivo-ctid',
                                                s.service_id,
                                                s.service_addr,
                                                9495,
                                                [u'tag_1', u'tag_2'])

        assert_that(service, equal_to(expected))


class BaseFinderTestCase(unittest.TestCase):

    def setUp(self):
        self.remote_tokens = {'dc1': 'dc1-token',
                              'dc2': 'dc2-token'}
        self.consul_config = {'token': 'master-token',
                              'scheme': 'http',
                              'port': 8500,
                              'host': 'localhost',
                              'verify': True}


class TestRemoteServiceFinderFilterHealthServices(BaseFinderTestCase):

    def test_that_no_service_id_is_not_included(self):
        nodes = [{'Checks': [{'ServiceID': '', 'ServiceName': 'foobar'},
                             {'ServiceID': 'theserviceid', 'ServiceName': 'foobar'}]}]

        finder = remote_service.Finder(self.consul_config, self.remote_tokens)

        result = finder._filter_health_services('foobar', nodes)

        assert_that(result, contains('theserviceid'))

    def test_that_other_service_name_is_not_included(self):
        nodes = [{'Checks': [{'ServiceID': 1, 'ServiceName': 'other'},
                             {'ServiceID': 2, 'ServiceName': 'foobar'}]}]

        finder = remote_service.Finder(self.consul_config, self.remote_tokens)

        result = finder._filter_health_services('foobar', nodes)

        assert_that(result, contains(2))


@patch('xivo_cti.remote_service.requests')
class TestRemoteServiceFinderGetDatacenters(BaseFinderTestCase):

    def test_that_the_url_matches_the_config(self, requests):
        requests.get.return_value = Mock(status_code=200)
        url_and_configs = [
            ('http://localhost:8500/v1/catalog/datacenters', self.consul_config),
            ('https://192.168.1.1:2155/v1/catalog/datacenters', {'scheme': 'https',
                                                                 'host': '192.168.1.1',
                                                                 'port': 2155}),
        ]

        for url, config in url_and_configs:
            finder = remote_service.Finder(config, self.remote_tokens)
            finder._get_datacenters()
            requests.get.assert_called_once_with(url, verify=ANY)
            requests.reset_mock()

    def test_that_raises_if_not_200(self, requests):
        requests.get.return_value = Mock(status_code=403, text='some error')

        finder = remote_service.Finder(self.consul_config, self.remote_tokens)

        assert_that(calling(finder._get_datacenters), raises(Exception))

    def test_that_health_uses_the_configured_verify(self, requests):
        requests.get.return_value = Mock(status_code=200)
        verify_and_configs = [
            (True, self.consul_config),
            (False, {'verify': False, 'scheme': 'https', 'host': '192.168.1.1', 'port': 2155}),
        ]

        for verify, config in verify_and_configs:
            finder = remote_service.Finder(config, self.remote_tokens)
            finder._get_datacenters()
            requests.get.assert_called_once_with(ANY, verify=verify)
            requests.reset_mock()


@patch('xivo_cti.remote_service.requests')
class TestRemoteServiceFinderGetHealthy(BaseFinderTestCase):

    def test_that_get_healthy_uses_the_configured_dc_token(self, requests):
        requests.get.return_value = Mock(status_code=200)

        finder = remote_service.Finder(self.consul_config, self.remote_tokens)

        for dc, token in [('dc1', 'dc1-token'), ('dc3', 'master-token')]:
            with patch.object(finder, '_filter_health_services'):
                finder._get_healthy('foobar', dc)
            expected = {'X-Consul-Token': token}
            requests.get.assert_called_once_with(ANY,
                                                 headers=expected,
                                                 verify=ANY,
                                                 params=ANY)
            requests.reset_mock()

    def test_that_the_health_url_matches_the_config(self, requests):
        requests.get.return_value = Mock(status_code=200)
        url_and_configs = [
            ('http://localhost:8500/v1/health/service/foobar', self.consul_config),
            ('https://192.168.1.1:2155/v1/health/service/foobar', {'scheme': 'https',
                                                                   'host': '192.168.1.1',
                                                                   'port': 2155}),
        ]

        for url, config in url_and_configs:
            finder = remote_service.Finder(config, self.remote_tokens)
            with patch.object(finder, '_filter_health_services'):
                finder._get_healthy('foobar', s.dc)
            requests.get.assert_called_once_with(url, headers=ANY, verify=ANY, params=ANY)
            requests.reset_mock()

    def test_that_health_uses_the_configured_verify(self, requests):
        requests.get.return_value = Mock(status_code=200)
        verify_and_configs = [
            (True, self.consul_config),
            (False, {'verify': False, 'scheme': 'https', 'host': '192.168.1.1', 'port': 2155}),
        ]

        for verify, config in verify_and_configs:
            finder = remote_service.Finder(config, self.remote_tokens)
            with patch.object(finder, '_filter_health_services'):
                finder._get_healthy('foobar', s.dc)
            requests.get.assert_called_once_with(ANY, headers=ANY, verify=verify, params=ANY)
            requests.reset_mock()

    def test_that_return_results_filtered_by_filter_health_services(self, requests):
        requests.get.return_value = Mock(status_code=200)
        finder = remote_service.Finder(self.consul_config, self.remote_tokens)

        with patch.object(finder, '_filter_health_services') as filter_:
            result = finder._get_healthy('foobar', s.dc)

        filter_.assert_called_once_with('foobar', requests.get().json.return_value)
        assert_that(result, equal_to(filter_.return_value))

    def test_that_params_are_based_on_the_datacenter(self, requests):
        requests.get.return_value = Mock(status_code=200)

        finder = remote_service.Finder(self.consul_config, self.remote_tokens)

        for dc in ['dc1', 'dc2']:
            with patch.object(finder, '_filter_health_services'):
                finder._get_healthy('foobar', dc)
            expected = {'dc': dc, 'passing': True}
            requests.get.assert_called_once_with(ANY,
                                                 headers=ANY,
                                                 verify=ANY,
                                                 params=expected)
            requests.reset_mock()

    def test_that_raises_if_not_200(self, requests):
        requests.get.return_value = Mock(status_code=403, text='some error')

        finder = remote_service.Finder(self.consul_config, self.remote_tokens)

        assert_that(calling(finder._get_healthy).with_args('foobar', 'dc1'),
                    raises(Exception))


class TestRemoteServiceFinderListHealthyServices(BaseFinderTestCase):

    def test_that_all_datacenters_are_searched(self):
        dcs = ['dc1', 'dc2', 'dc3']

        finder = remote_service.Finder(self.consul_config, self.remote_tokens)

        with patch.object(finder, '_get_datacenters', Mock(return_value=dcs)):
            with patch.object(finder, '_get_healthy') as get_healthy:
                with patch.object(finder, '_list_services') as list_services:
                    finder.list_healthy_services(s.service_name)

        for dc in dcs:
            get_healthy.assert_any_call(s.service_name, dc)
            list_services.assert_any_call(s.service_name, dc)

    def test_that_only_healthy_services_are_returned(self):
        s1, s2 = services = [
            {'ServiceID': 1},
            {'ServiceID': 42},
        ]

        finder = remote_service.Finder(self.consul_config, self.remote_tokens)

        with patch.object(finder, '_get_datacenters', Mock(return_value=['dc1'])):
            with patch.object(finder, '_get_healthy', Mock(return_value=[42])):
                with patch.object(finder, '_list_services', Mock(return_value=services)):
                    result = finder.list_healthy_services(s.service_name)

        assert_that(result, contains(s2))


@patch('xivo_cti.remote_service.requests')
class TestRemoteServiceFinderListServices(BaseFinderTestCase):

    def test_that_uses_the_configured_dc_token(self, requests):
        requests.get.return_value = Mock(status_code=200)
        finder = remote_service.Finder(self.consul_config, self.remote_tokens)

        for dc, token in [('dc1', 'dc1-token'), ('dc3', 'master-token')]:
            finder._list_services('foobar', dc)
            expected = {'X-Consul-Token': token}
            requests.get.assert_called_once_with(ANY,
                                                 headers=expected,
                                                 verify=ANY,
                                                 params=ANY)
            requests.reset_mock()

    def test_that_url_matches_the_config(self, requests):
        requests.get.return_value = Mock(status_code=200)
        url_and_configs = [
            ('http://localhost:8500/v1/catalog/service/foobar', self.consul_config),
            ('https://192.168.1.1:2155/v1/catalog/service/foobar', {'scheme': 'https',
                                                                   'host': '192.168.1.1',
                                                                   'port': 2155}),
        ]

        for url, config in url_and_configs:
            finder = remote_service.Finder(config, self.remote_tokens)
            finder._list_services('foobar', s.dc)
            requests.get.assert_called_once_with(url, headers=ANY, verify=ANY, params=ANY)
            requests.reset_mock()

    def test_that_uses_the_configured_verify(self, requests):
        requests.get.return_value = Mock(status_code=200)
        verify_and_configs = [
            (True, self.consul_config),
            (False, {'verify': False, 'scheme': 'https', 'host': '192.168.1.1', 'port': 2155}),
        ]

        for verify, config in verify_and_configs:
            finder = remote_service.Finder(config, self.remote_tokens)
            finder._list_services('foobar', s.dc)
            requests.get.assert_called_once_with(ANY, headers=ANY, verify=verify, params=ANY)
            requests.reset_mock()

    def test_that_results_is_the_returned_json(self, requests):
        requests.get.return_value = Mock(status_code=200)
        finder = remote_service.Finder(self.consul_config, self.remote_tokens)

        result = finder._list_services('foobar', s.dc)

        assert_that(result, equal_to(requests.get().json.return_value))

    def test_that_params_are_based_on_the_datacenter(self, requests):
        requests.get.return_value = Mock(status_code=200)

        finder = remote_service.Finder(self.consul_config, self.remote_tokens)

        for dc in ['dc1', 'dc2']:
            finder._list_services('foobar', dc)
            expected = {'dc': dc}
            requests.get.assert_called_once_with(ANY,
                                                 headers=ANY,
                                                 verify=ANY,
                                                 params=expected)
            requests.reset_mock()

    def test_that_raises_if_not_200(self, requests):
        requests.get.return_value = Mock(status_code=403, text='some error')

        finder = remote_service.Finder(self.consul_config, self.remote_tokens)

        assert_that(calling(finder._list_services).with_args('foobar', 'dc1'),
                    raises(Exception))


class TestRemoteServiceTracker(unittest.TestCase):

    def setUp(self):
        self.uuid = 'e4d147b6-f747-4b64-955d-8c36fbcd1d3f'
        self.tracker = remote_service.RemoteServiceTracker({'host': s.consul_host,
                                                            'port': s.consul_port,
                                                            'token': s.consul_token},
                                                           'local-uuid',
                                                           6666)

        self.foobar_service = remote_service.RemoteService('foobar',
                                                           s.service_id,
                                                           s.foobar_host,
                                                           s.foobar_port,
                                                           [s.tag_1])

    def test_that_the_remote_service_tracker_knows_about_itself(self):
        services = self.tracker.list_services_with_uuid('xivo-ctid', 'local-uuid')

        assert_that(services[0].to_dict(), equal_to({'host': 'localhost',
                                                     'port': 6666}))

    def test_fetch_services_will_query_all_datacenters(self):
        data_centers = ['dc1', 'dc2']
        s1 = {u'Node': u'dc1',
              u'ServiceName': u'xivo-ctid',
              u'ServicePort': 9495,
              u'ServiceID': s.service_id_1,
              u'ServiceAddress': s.service_addr_1,
              u'Address': u'127.0.0.1',
              u'ServiceTags': [u'tag_1', u'tag_2', self.uuid]}
        s2 = {u'Node': u'dc2',
              u'ServiceName': u'xivo-ctid',
              u'ServicePort': 9495,
              u'ServiceID': s.service_id_2,
              u'ServiceAddress': s.service_addr_2,
              u'Address': u'127.0.0.1',
              u'ServiceTags': [u'tag_1', u'tag_2', self.uuid]}

        with patch.object(self.tracker, '_consul_client') as consul_client:
            catalog = consul_client.return_value.catalog
            catalog.datacenters.return_value = data_centers
            catalog.service.side_effect = lambda s, dc: ('index', [{'dc1': s1,
                                                                    'dc2': s2}.get(dc)])

            services = self.tracker.fetch_services('foobar', self.uuid)

            assert_that(services, contains(remote_service.RemoteService.from_consul_service(s1),
                                           remote_service.RemoteService.from_consul_service(s2)))

    def test_fetch_services_will_not_track_duplicates(self):
        data_centers = ['dc1', 'dc2']
        s1 = {u'Node': u'dc1',
              u'ServiceName': u'xivo-ctid',
              u'ServicePort': 9495,
              u'ServiceID': s.service_id_1,
              u'ServiceAddress': s.service_addr_1,
              u'Address': u'127.0.0.1',
              u'ServiceTags': [u'tag_1', u'tag_2', self.uuid]}
        s2 = {u'Node': u'dc2',
              u'ServiceName': u'xivo-ctid',
              u'ServicePort': 9495,
              u'ServiceID': s.service_id_2,
              u'ServiceAddress': s.service_addr_2,
              u'Address': u'127.0.0.1',
              u'ServiceTags': [u'tag_1', u'tag_2', self.uuid]}

        with patch.object(self.tracker, '_consul_client') as consul_client:
            catalog = consul_client.return_value.catalog
            catalog.datacenters.return_value = data_centers
            # each config is returned twice
            catalog.service.side_effect = lambda s, dc: ('index', map({'dc1': s1,
                                                                       'dc2': s2}.get, [dc, dc]))

            services = self.tracker.fetch_services('foobar', self.uuid)

            assert_that(services, contains(remote_service.RemoteService.from_consul_service(s1),
                                           remote_service.RemoteService.from_consul_service(s2)))

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
