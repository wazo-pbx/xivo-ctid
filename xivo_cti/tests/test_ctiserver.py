# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from xivo_cti.ctiserver import CTIServer
from mock import Mock
from xivo_cti.cti_config import Config


class TestCTIServer(unittest.TestCase):

    def test_send_cti_event(self):
        event = {'event': 'My test event'}
        server = CTIServer(Mock(Config))

        server.send_cti_event(event)

        self.assertEqual(len(server._cti_events), 1)
        result = server._cti_events.popleft()

        self.assertEqual(result, event)
