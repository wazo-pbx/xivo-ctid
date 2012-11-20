# -*- coding: utf-8 -*-

# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall'
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import mock

from xivo_cti import dao
from xivo_cti.services.device.manager import DeviceManager
from xivo_cti.services.device.controller.aastra import AastraController
from xivo_cti.dao.device_dao import DeviceDAO


class TestDeviceManager(unittest.TestCase):

    def setUp(self):
        dao.device = mock.Mock(DeviceDAO)
        self.aastra_controller = mock.Mock(AastraController)

    def test_answer(self):
        device_id = 13
        formatted_answer_ami_command = 'answer the phone'
        self.aastra_controller.answer.return_value = formatted_answer_ami_command
        manager = DeviceManager()
        manager.aastra_controller = self.aastra_controller
        manager.send_ami = mock.Mock()
        manager.is_supported_device = mock.Mock(return_value=True)

        manager.answer(device_id)

        self.aastra_controller.answer.assert_called_once_with(device_id)
        manager.send_ami.assert_called_once_with(formatted_answer_ami_command)

    def test_answer_from_good_device_manager(self):
        device_id = 13
        formatted_answer_ami_command = 'aastra_specific_answer'
        self.aastra_controller.answer.return_value = formatted_answer_ami_command
        manager = DeviceManager()
        manager.aastra_controller = self.aastra_controller
        manager.send_ami = mock.Mock()
        manager.is_supported_device = mock.Mock(return_value=True)

        manager.answer(device_id)

        self.aastra_controller.answer.assert_called_once_with(device_id)
        manager.send_ami.assert_called_once_with(formatted_answer_ami_command)

    def test_answer_with_unsupported_device(self):
        device_id = 13
        formatted_answer_ami_command = 'aastra_specific_answer'
        self.aastra_controller.answer.return_value = formatted_answer_ami_command
        manager = DeviceManager()
        manager.aastra_controller = self.aastra_controller
        manager.send_ami = mock.Mock()
        manager.is_supported_device = mock.Mock(return_value=False)

        manager.answer(device_id)

        manager.is_supported_device.assert_called_once_with(device_id)

        self.assertEquals(manager.send_ami.call_count, 0)
        self.assertEquals(self.aastra_controller.answer.call_count, 0)

    def test_is_supported_device_6757i(self):
        device_id = 13
        vendor = 'Aastra'
        model = '6757i'

        dao.device.get_vendor_model.return_value = vendor, model

        self.manager = DeviceManager()
        result = self.manager.is_supported_device(device_id)

        self.assertEqual(result, True)

    def test_is_supported_device_6755i(self):
        device_id = 13
        vendor = 'Aastra'
        model = '6755i'

        dao.device.get_vendor_model.return_value = vendor, model

        self.manager = DeviceManager()
        result = self.manager.is_supported_device(device_id)

        self.assertEqual(result, True)

    def test_is_not_supported_device(self):
        device_id = 13
        vendor = 'Cisco'
        model = '1234'

        dao.device.get_vendor_model.return_value = vendor, model

        self.manager = DeviceManager()
        result = self.manager.is_supported_device(device_id)

        self.assertEqual(result, False)
