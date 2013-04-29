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

from xivo_cti.cti.commands.dial import Dial
from hamcrest import *


class TestDial(unittest.TestCase):

    def setUp(self):
        self._commandid = 125708937534
        self._exten = '1234'
        self.dial_message = {
            'class': 'ipbxcommand',
            'command': 'dial',
            'commandid': self._commandid,
            'destination': self._exten,
        }

    def test_from_dict_url_style_destination(self):
        self.dial_message['destionation'] = 'exten:xivo/' + self._exten
        dial = Dial.from_dict(self.dial_message)

        assert_that(dial.commandid, equal_to(self._commandid), 'Command ID')
        assert_that(dial.exten, equal_to(self._exten), 'Dialed extension')

    def test_from_dict_other_destination(self):
        dial = Dial.from_dict(self.dial_message)

        assert_that(dial.commandid, equal_to(self._commandid), 'Command ID')
        assert_that(dial.exten, equal_to(self._exten), 'Dialed extension')
