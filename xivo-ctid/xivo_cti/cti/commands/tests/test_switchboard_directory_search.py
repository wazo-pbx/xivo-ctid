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

from xivo_cti.cti.commands.switchboard_directory_search import SwitchboardDirectorySearch
from xivo_cti.cti.cti_command import CTICommand


class TestSwitchboardDirectorySearch(unittest.TestCase):

    _command_id = 1171069123
    _pattern = 'dkfj'
    _msg_dict = {CTICommand.CLASS: SwitchboardDirectorySearch.COMMAND_CLASS,
                 CTICommand.COMMANDID: _command_id,
                 SwitchboardDirectorySearch.PATTERN: _pattern}

    def test_switchboard_directory_search(self):
        self.assertEqual(SwitchboardDirectorySearch.COMMAND_CLASS, 'switchboard_directory_search')

        switchboard_directory_search = SwitchboardDirectorySearch()

        self.assertEqual(switchboard_directory_search.command_class, SwitchboardDirectorySearch.COMMAND_CLASS)
        self.assertEqual(switchboard_directory_search.commandid, None)
        self.assertEqual(switchboard_directory_search.pattern, None)

    def test_from_dict(self):
        switchboard_directory_search = SwitchboardDirectorySearch.from_dict(self._msg_dict)

        self.assertEqual(switchboard_directory_search.command_class, SwitchboardDirectorySearch.COMMAND_CLASS)
        self.assertEqual(switchboard_directory_search.commandid, self._command_id)
        self.assertEqual(switchboard_directory_search.pattern, self._pattern)
