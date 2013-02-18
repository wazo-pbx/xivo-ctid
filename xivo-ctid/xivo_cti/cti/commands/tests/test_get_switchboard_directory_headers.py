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

from xivo_cti.cti.commands.get_switchboard_directory_headers import GetSwitchboardDirectoryHeaders


class TestGetSwitchboardDirectoryHeader(unittest.TestCase):

    def setUp(self):
        self.commandid = 125731893
        self.message = {
            'class': 'get_switchboard_directory_headers',
            'commandid': self.commandid,
        }

    def test_GetSwitchboardDirectoryHeaders(self):
        self.assertEqual(GetSwitchboardDirectoryHeaders.COMMAND_CLASS, 'get_switchboard_directory_headers')

    def test_from_dict(self):
        msg = GetSwitchboardDirectoryHeaders.from_dict(self.message)

        self.assertEqual(msg.commandid, self.commandid)
