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

from hamcrest import assert_that, contains, equal_to, is_not
from xivo_cti.services.bridge.bridge import Bridge


class BridgeTest(unittest.TestCase):

    def setUp(self):
        self.bridge = Bridge('e136cd36-5187-430c-af2a-d1f08870847b', 'basic')

    def test_add_channel(self):
        channel_name = 'SIP/n5ksoc-00000001'
        self.bridge.add_channel(channel_name)

        assert_that(self.bridge.channels, contains(channel_name))

    def test_remove_channel(self):
        channel_name = 'SIP/n5ksoc-00000001'
        self.bridge.add_channel(channel_name)
        self.bridge.remove_channel(channel_name)

        assert_that(self.bridge.channels, is_not(contains(channel_name)))

    def test_remove_channel_non_existent(self):
        channel_name = 'SIP/n5ksoc-00000001'
        self.bridge.remove_channel(channel_name)

        assert_that(self.bridge.channels, is_not(contains(channel_name)))

    def test_basic_channels_connected_return_true_with_two_basic_channels(self):
        self.bridge.channels = ['SIP/n5ksoc-00000001', 'SIP/n5ksoc-00000002']

        assert_that(self.bridge.basic_channels_connected())

    def test_basic_channels_connected_return_false_when_one_basic_channels(self):
        self.bridge.channels = ['SIP/n5ksoc-00000001']

        assert_that(self.bridge.basic_channels_connected(), equal_to(False))
