# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, patch

from xivo_cti.provd import CTIProvdClient
from xivo_cti.services.device.manager import DeviceManager
from xivo_cti.services.device.controller.aastra import AastraController
from xivo_cti.services.device.controller.base import BaseController
from xivo_cti.services.device.controller.polycom import PolycomController
from xivo_cti.services.device.controller.snom import SnomController
from xivo_cti.services.device.controller.yealink import YealinkController
from xivo_cti.xivo_ami import AMIClass


class TestDeviceManager(unittest.TestCase):

    POLYCOM_CONFIG = {
        'switchboard_polycom': {
            'username': 'xivo_switchboard',
            'password': 'xivo_switchboard',
            'answer_delay': 0.4,
        },
    }
    SNOM_CONFIG = {
        'switchboard_snom': {
            'username': 'guest',
            'password': 'guest',
            'answer_delay': 0.5,
        },
    }

    def setUp(self):
        self.ami_class = Mock(AMIClass)
        self.cti_provd_client = Mock(CTIProvdClient)
        self._base_controller = Mock(BaseController)
        self._aastra_controller = Mock(AastraController)
        self._polycom_controller = Mock(PolycomController)
        self._snom_controller = Mock(SnomController)
        self._yealink_controller = Mock(YealinkController)
        with patch('xivo_cti.services.device.controller.polycom.config', self.POLYCOM_CONFIG),\
                patch('xivo_cti.services.device.controller.snom.config', self.SNOM_CONFIG):
            self.manager = DeviceManager(self.ami_class, self.cti_provd_client)

    def test_get_answer_fn_no_device(self):
        self.manager._base_controller = self._base_controller
        self.cti_provd_client.find_device.return_value = None

        self.manager.get_answer_fn(5)()

        self._base_controller.answer.assert_called_once_with(None)

    def test_get_answer_fn_not_supported(self):
        device = Mock()
        device.is_switchboard.return_value = False
        self.cti_provd_client.find_device.return_value = device
        self.manager._base_controller = self._base_controller

        self.manager.get_answer_fn(device.id)()

        self.cti_provd_client.find_device.assert_called_once_with(device.id)
        self._base_controller.answer.assert_called_once_with(device)

    def test_get_answer_fn_switchboard_but_unknown_vendor(self):
        device = Mock()
        device.is_switchboard.return_value = True
        device.vendor = 'BMW'
        self.cti_provd_client.find_device.return_value = device
        self.manager._base_controller = self._base_controller

        self.manager.get_answer_fn(device.id)()

        self._base_controller.answer.assert_called_once_with(device)

    def test_get_answer_fn_aastra_switchboard(self):
        device = Mock()
        device.is_switchboard.return_value = True
        device.vendor = 'Aastra'
        self.cti_provd_client.find_device.return_value = device
        self.manager._aastra_controller = self._aastra_controller

        self.manager.get_answer_fn(device.id)()

        self._aastra_controller.answer.assert_called_once_with(device)

    def test_get_answer_fn_polycom_switchboard(self):
        device = Mock()
        device.is_switchboard.return_value = True
        device.vendor = 'Polycom'
        self.cti_provd_client.find_device.return_value = device
        self.manager._polycom_controller = self._polycom_controller

        self.manager.get_answer_fn(device.id)()

        self._polycom_controller.answer.assert_called_once_with(device)

    def test_get_answer_fn_snom_switchboard(self):
        device = Mock()
        device.is_switchboard.return_value = True
        device.vendor = 'Snom'
        self.cti_provd_client.find_device.return_value = device
        self.manager._snom_controller = self._snom_controller

        self.manager.get_answer_fn(device.id)()

        self._snom_controller.answer.assert_called_once_with(device)

    def test_get_answer_fn_yealink_switchboard(self):
        device = Mock()
        device.is_switchboard.return_value = True
        device.vendor = 'Yealink'
        self.cti_provd_client.find_device.return_value = device
        self.manager._yealink_controller = self._yealink_controller

        self.manager.get_answer_fn(device.id)()

        self._yealink_controller.answer.assert_called_once_with(device)
