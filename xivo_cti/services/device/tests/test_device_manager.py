# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

from mock import patch
from mock import Mock

from xivo_cti.services.device.manager import DeviceManager
from xivo_cti.services.device.controller.aastra import AastraController
from xivo_cti.services.device.controller.base import BaseController
from xivo_cti.services.device.controller.snom import SnomController
from xivo_cti.services.device.controller.yealink import YealinkController
from xivo_dao.data_handler.exception import NotFoundError
from xivo_cti.xivo_ami import AMIClass


class TestDeviceManager(unittest.TestCase):

    def setUp(self):
        self.ami_class = Mock(AMIClass)
        self._base_controller = Mock(BaseController)
        self._aastra_controller = Mock(AastraController)
        self._snom_controller = Mock(SnomController)
        self._yealink_controller = Mock(YealinkController)
        self.manager = DeviceManager(self.ami_class)

    @patch('xivo_dao.data_handler.device.services.get',
           Mock(side_effect=NotFoundError()))
    def test_get_answer_fn_no_device(self):
        self.manager._base_controller = self._base_controller

        self.manager.get_answer_fn(5)()

        self._base_controller.answer.assert_called_once_with(None)

    @patch('xivo_dao.data_handler.device.services.get')
    def test_get_answer_fn_not_supported(self, mock_device_service_get):
        device = Mock()
        device.is_switchboard.return_value = False
        mock_device_service_get.return_value = device
        self.manager._base_controller = self._base_controller

        self.manager.get_answer_fn(device.id)()

        self._base_controller.answer.assert_called_once_with(device)

    @patch('xivo_dao.data_handler.device.services.get')
    def test_get_answer_fn_switchboard_but_unknown_vendor(self, mock_device_service_get):
        device = Mock()
        device.is_switchboard.return_value = True
        device.vendor = 'BMW'
        mock_device_service_get.return_value = device
        self.manager._base_controller = self._base_controller

        self.manager.get_answer_fn(device.id)()

        self._base_controller.answer.assert_called_once_with(device)

    @patch('xivo_dao.data_handler.device.services.get')
    def test_get_answer_fn_aastra_switchboard(self, mock_device_service_get):
        device = Mock()
        device.is_switchboard.return_value = True
        device.vendor = 'Aastra'
        mock_device_service_get.return_value = device
        self.manager._aastra_controller = self._aastra_controller

        self.manager.get_answer_fn(device.id)()

        self._aastra_controller.answer.assert_called_once_with(device)

    @patch('xivo_dao.data_handler.device.services.get')
    def test_get_answer_fn_snom_switchboard(self, mock_device_service_get):
        device = Mock()
        device.is_switchboard.return_value = True
        device.vendor = 'Snom'
        mock_device_service_get.return_value = device
        self.manager._snom_controller = self._snom_controller

        self.manager.get_answer_fn(device.id)()

        self._snom_controller.answer.assert_called_once_with(device)

    @patch('xivo_dao.data_handler.device.services.get')
    def test_get_answer_fn_yealink_switchboard(self, mock_device_service_get):
        device = Mock()
        device.is_switchboard.return_value = True
        device.vendor = 'Yealink'
        mock_device_service_get.return_value = device
        self.manager._yealink_controller = self._yealink_controller

        self.manager.get_answer_fn(device.id)()

        self._yealink_controller.answer.assert_called_once_with(device)
