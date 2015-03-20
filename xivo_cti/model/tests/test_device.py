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

from hamcrest import assert_that, is_not

from xivo_cti.model.device import Device


class TestDevice(unittest.TestCase):

    def setUp(self):
        self.device = Device(75)

    def test_is_switchboard_plugin_name(self):
        self.device.plugin = 'xivo-aastra-switchboard'

        assert_that(self.device.is_switchboard())

    def test_is_switchboard_no_plugin(self):
        assert_that(is_not(self.device.is_switchboard()))

    def test_is_switchboard_option_true(self):
        self.device.options = {'switchboard': True}

        assert_that(self.device.is_switchboard())

    def test_is_switchboard_option_false(self):
        self.device.options = {'switchboard': False}

        assert_that(is_not(self.device.is_switchboard()))

    def test_is_switchboard_no_option(self):
        self.device.options = {}

        assert_that(is_not(self.device.is_switchboard()))

    def test_new_from_provd_device_minimal(self):
        provd_device = {'id': '123'}

        device = Device.new_from_provd_device(provd_device)

        self.assertEqual(device.id, '123')

    def test_new_from_provd_device(self):
        ip = '169.254.1.1'
        plugin = 'xivo-foobar'
        vendor = 'Acme'
        options = {}
        provd_device = {
            'id': '123',
            'ip': ip,
            'plugin': plugin,
            'vendor': vendor,
            'options': options,
        }

        device = Device.new_from_provd_device(provd_device)

        self.assertEqual(device.ip, ip)
        self.assertEqual(device.plugin, plugin)
        self.assertEqual(device.vendor, vendor)
        self.assertEqual(device.options, options)
