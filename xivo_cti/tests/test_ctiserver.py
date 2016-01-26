# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
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
from xivo_cti.ctiserver import CTIServer
from xivo_cti.cti.cti_group import CTIGroup


class TestCTIServer(unittest.TestCase):

    def setUp(self):
        self.broadcast_cti_group = Mock(CTIGroup)
        self.bus_publisher = Mock()
        self.cti_server = CTIServer(self.bus_publisher)
        self.cti_server._broadcast_cti_group = self.broadcast_cti_group

    def test_send_cti_event(self):
        event = {'event': 'My test event'}

        self.cti_server.send_cti_event(event)

        self.broadcast_cti_group.send_message.assert_called_once_with(event)
