# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from xivo_cti.provd import CTIProvdClient
from wazo_provd_client.exceptions import ProvdError


class TestCTIProvdClient(unittest.TestCase):

    def setUp(self):
        self.provd_client = Mock()
        self.provd_dev_mgr = self.provd_client.devices
        self.cti_provd_client = CTIProvdClient(self.provd_client)
        self.device_id = 'foobar'
        self.provd_device = {'id': self.device_id}

    def test_find_device(self):
        self.provd_dev_mgr.get.return_value = self.provd_device

        device = self.cti_provd_client.find_device(self.device_id)

        self.provd_dev_mgr.get.assert_called_once_with(self.device_id)
        self.assertEqual(device.id, self.device_id)

    def test_find_device_not_found(self):
        self.provd_dev_mgr.get.side_effect = ProvdError(Mock(status_code=404, message='not found'))

        device = self.cti_provd_client.find_device(self.device_id)

        self.assertIs(device, None)

    def test_find_device_other_error(self):
        self.provd_dev_mgr.get.side_effect = Exception()

        device = self.cti_provd_client.find_device(self.device_id)

        self.assertIs(device, None)
