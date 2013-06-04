# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from xivo_cti.services.call import helper


class TestCallHelper(unittest.TestCase):

    def test_interface_from_channel_sip(self):
        channel = 'SIP/askdjhf-3216549'
        expected_interface = 'SIP/askdjhf'

        result = helper.interface_from_channel(channel)

        self.assertEquals(expected_interface, result)

    def test_interface_from_channel_sccp(self):
        channel = 'sccp/13486@SEP6556DEADBEEF-658'
        expected_interface = 'sccp/13486@SEP6556DEADBEEF'

        result = helper.interface_from_channel(channel)

        self.assertEquals(expected_interface, result)
