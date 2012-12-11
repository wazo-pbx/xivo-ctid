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

from mock import patch, Mock

from xivo_cti.services.device.manager import DeviceManager
from xivo_cti.services.device.controller.aastra import AastraController
from xivo_cti.xivo_ami import AMIClass


class TestDeviceManager(unittest.TestCase):

    def setUp(self):
        self.aastra_controller = mock.Mock(AastraController)
        ami_class = Mock(AMIClass)
        self.manager = DeviceManager(ami_class)
        self.manager.aastra_controller = self.aastra_controller

    def test_answer(self):
        device_id = 13
        formatted_answer_ami_command = 'peer', {'var': 'val'}
        self.aastra_controller.answer.return_value = formatted_answer_ami_command
        self.manager.send_sipnotify = mock.Mock()
        self.manager.is_supported_device = mock.Mock(return_value=True)

        self.manager.answer(device_id)

        self.aastra_controller.answer.assert_called_once_with(device_id)
        self.manager.send_sipnotify.assert_called_once_with(formatted_answer_ami_command)

    def test_answer_from_good_device_manager(self):
        device_id = 13
        formatted_answer_ami_command = 'peer', {'var': 'val'}
        self.aastra_controller.answer.return_value = formatted_answer_ami_command
        self.manager.send_sipnotify = mock.Mock()
        self.manager.is_supported_device = mock.Mock(return_value=True)

        self.manager.answer(device_id)

        self.aastra_controller.answer.assert_called_once_with(device_id)
        self.manager.send_sipnotify.assert_called_once_with(formatted_answer_ami_command)

    def test_answer_with_unsupported_device(self):
        device_id = 13
        formatted_answer_ami_command = 'peer', {'var': 'val'}
        self.aastra_controller.answer.return_value = formatted_answer_ami_command
        self.manager.send_sipnotify = mock.Mock()
        self.manager.is_supported_device = mock.Mock(return_value=False)

        self.manager.answer(device_id)

        self.manager.is_supported_device.assert_called_once_with(device_id)

        self.assertEquals(self.manager.send_sipnotify.call_count, 0)
        self.assertEquals(self.aastra_controller.answer.call_count, 0)

    @patch('xivo_dao.device_dao.get_vendor_model')
    def test_is_supported_device_6757i(self, mock_get_vendor_model):
        device_id = 13
        vendor = 'Aastra'
        model = '6757i'

        mock_get_vendor_model.return_value = vendor, model

        result = self.manager.is_supported_device(device_id)

        self.assertEqual(result, True)

    @patch('xivo_dao.device_dao.get_vendor_model')
    def test_is_supported_device_6755i(self, mock_get_vendor_model):
        device_id = 13
        vendor = 'Aastra'
        model = '6755i'

        mock_get_vendor_model.return_value = vendor, model

        result = self.manager.is_supported_device(device_id)

        self.assertEqual(result, True)

    @patch('xivo_dao.device_dao.get_vendor_model')
    def test_is_not_supported_device(self, mock_get_vendor_model):
        device_id = 13
        vendor = 'Cisco'
        model = '1234'

        mock_get_vendor_model.return_value = vendor, model

        result = self.manager.is_supported_device(device_id)

        self.assertEqual(result, False)

    def test_send_sipnotify(self):
        channel, vars = 'SIP/abc', {'un': 1}
        cmd = channel, vars

        self.manager.send_sipnotify(cmd)

        self.manager.ami.sipnotify.assert_called_once_with(channel, vars)
