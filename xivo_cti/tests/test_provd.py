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

from mock import Mock
from mock import patch

from xivo_cti.provd import CTIProvdClient
from xivo_provd_client import NotFoundError


class TestCTIProvdClient(unittest.TestCase):

    def setUp(self):
        self.provd_client = Mock()
        self.provd_dev_mgr = self.provd_client.device_manager()
        self.cti_provd_client = CTIProvdClient(self.provd_client)
        self.device_id = 'foobar'
        self.provd_device = {'id': self.device_id}

    def test_find_device(self):
        self.provd_dev_mgr.get.return_value = self.provd_device

        device = self.cti_provd_client.find_device(self.device_id)

        self.provd_dev_mgr.get.assert_called_once_with(self.device_id)
        self.assertEqual(device.id, self.device_id)

    def test_find_device_not_found(self):
        self.provd_dev_mgr.get.side_effect = NotFoundError()

        device = self.cti_provd_client.find_device(self.device_id)

        self.assertIs(device, None)

    def test_find_device_other_error(self):
        self.provd_dev_mgr.get.side_effect = Exception()

        device = self.cti_provd_client.find_device(self.device_id)

        self.assertIs(device, None)

    @patch('xivo_cti.provd.new_provisioning_client')
    def test_new_from_config_minimal(self, mock_new_provisioning_client):
        provd_config = {}

        cti_provd_client = CTIProvdClient.new_from_config(provd_config)

        expected_url = 'http://localhost:8666/provd'
        mock_new_provisioning_client.assert_called_once_with(expected_url, None)
        self.assertIsInstance(cti_provd_client, CTIProvdClient)

    @patch('xivo_cti.provd.new_provisioning_client')
    def test_new_from_config_full(self, mock_new_provisioning_client):
        provd_config = {
            'host': 'example.org',
            'port': 9999,
            'username': 'foo',
            'password': 'bar',
            'https': True,
        }

        cti_provd_client = CTIProvdClient.new_from_config(provd_config)

        expected_url = 'https://example.org:9999/provd'
        expected_credentials = ('foo', 'bar')
        mock_new_provisioning_client.assert_called_once_with(expected_url, expected_credentials)
        self.assertIsInstance(cti_provd_client, CTIProvdClient)

    @patch('xivo_cti.provd.logger')
    def test_new_from_config_unknown_param(self, mock_logger):
        provd_config = {
            'foo': 'bar',
        }

        CTIProvdClient.new_from_config(provd_config)

        self.assertTrue(mock_logger.warning.called)
