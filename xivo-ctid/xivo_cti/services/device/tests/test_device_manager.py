# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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
import mock

from hamcrest import assert_that
from hamcrest import equal_to
from mock import patch
from mock import Mock

from xivo_cti.services.device.manager import DeviceManager
from xivo_cti.services.device.controller.aastra import AastraController
from xivo_cti.services.device.controller.base import BaseController
from xivo_cti.services.device.controller.snom import SnomController
from xivo_dao.data_handler.device.model import Device
from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_cti.xivo_ami import AMIClass


class TestDeviceManager(unittest.TestCase):

    def setUp(self):
        self.ami_class = Mock(AMIClass)
        self._base_controller = Mock(BaseController)
        self._aastra_controller = Mock(AastraController)
        self._snom_controller = Mock(SnomController)
        self.manager = DeviceManager(self.ami_class)

    def test_is_supported_device_6731i(self):
        device = Device(
            id=13,
            vendor='Aastra',
            model='6731i',
            plugin='xivo-aastra-switchboard',
        )

        result = self.manager._is_supported_device(device)

        self.assertEqual(result, True)

    def test_is_supported_device_not_switchboard(self):
        device = Device(
            id=13,
            vendor='Aastra',
            model='6731i',
            plugin='xivo-aastra-3.2.2-SP3',
        )

        result = self.manager._is_supported_device(device)

        self.assertEqual(result, False)

    def test_is_supported_device_6757i(self):
        device = Device(
            id=13,
            vendor='Aastra',
            model='6757i',
            plugin='xivo-aastra-switchboard',
        )

        result = self.manager._is_supported_device(device)

        self.assertEqual(result, True)

    def test_is_supported_device_6755i(self):
        device = Device(
            id=13,
            vendor='Aastra',
            model='6755i',
            plugin='xivo-aastra-switchboard',
        )

        result = self.manager._is_supported_device(device)

        self.assertEqual(result, True)

    def test_is_supported_device_snom_720(self):
        device = Device(
            id=42,
            vendor='Snom',
            model='720',
            plugin='xivo-snom-switchboard',
        )

        result = self.manager._is_supported_device(device)

        self.assertEqual(result, True)

    def test_is_not_supported_device(self):
        device = Device(
            id=13,
            vendor='Cisco',
            model='1234',
            plugin='xivo-aastra-plugin',
        )

        result = self.manager._is_supported_device(device)

        self.assertEqual(result, False)

    def test_is_not_supported_device_missing_field(self):
        device = Device(
            id=13,
        )

        result = self.manager._is_supported_device(device)

        self.assertEqual(result, False)

    @patch('xivo_dao.data_handler.device.services.get')
    def test_get_answer_fn_not_supported(self, mock_device_service_get):
        device = Device(
            id=42,
            vendor='Cisco',
            model='1234',
            plugin='xivo-aastra-plugin',
        )
        mock_device_service_get.return_value = device
        self.manager._base_controller = self._base_controller

        self.manager.get_answer_fn(device.id)()

        self._base_controller.answer.assert_called_once_with(device)

    @patch('xivo_dao.data_handler.device.services.get',
           Mock(side_effect=ElementNotExistsError('Not found')))
    def test_get_answer_fn_no_device(self):
        self.manager._base_controller = self._base_controller

        self.manager.get_answer_fn(5)()

        self._base_controller.answer.assert_called_once_with(None)

    @patch('xivo_dao.data_handler.device.services.get')
    def test_get_answer_fn_aastra_switchboard(self, mock_device_service_get):
        device = Device(
            id=13,
            vendor='Aastra',
            model='6755i',
            plugin='xivo-aastra-switchboard',
        )
        mock_device_service_get.return_value = device
        self.manager._aastra_controller = self._aastra_controller

        self.manager.get_answer_fn(device.id)()

        self._aastra_controller.answer.assert_called_once_with(device)

    @patch('xivo_dao.data_handler.device.services.get')
    def test_get_answer_fn_snom_switchboard(self, mock_device_service_get):
        device = Device(
            id=13,
            vendor='Snom',
            model='720',
            plugin='xivo-snom-switchboard',
        )
        mock_device_service_get.return_value = device
        self.manager._snom_controller = self._snom_controller

        self.manager.get_answer_fn(device.id)()

        self._snom_controller.answer.assert_called_once_with(device)
