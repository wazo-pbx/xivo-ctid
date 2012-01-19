# vim: set fileencoding=utf-8 :
# XiVO CTI Server

# Copyright (C) 2007-2011  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from xivo_cti.cti.commands.getlist import GetList
from xivo_cti.cti.cti_command import CTICommand
from mock import Mock
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.cti.cti_command_handler import CTICommandHandler


class TestGetList(unittest.TestCase):

    _commandid = 1446226295
    _function = 'updateconfig'
    _list_name = 'users'
    _item_id = '1'
    _ipbx_id = 'xivo'
    _dict_msg = {CTICommand.CLASS: GetList.COMMAND_CLASS,
                 CTICommand.COMMANDID: _commandid,
                 GetList.FUNCTION: _function,
                 GetList.LIST_NAME: _list_name,
                 GetList.ITEM_ID: _item_id,
                 GetList.IPBX_ID: _ipbx_id}

    def test_get_list(self):
        self.assertEqual(GetList.COMMAND_CLASS, 'getlist')

        getlist = GetList()

        self.assertEqual(getlist.commandid, None)
        self.assertEqual(getlist.function, None)
        self.assertEqual(getlist.list_name, None)
        self.assertEqual(getlist.item_id, None)
        self.assertEqual(getlist.ipbx_id, None)

    def test_from_dict(self):
        getlist = GetList.from_dict(self._dict_msg)

        self.assertEqual(getlist.commandid, self._commandid)
        self.assertEqual(getlist.function, self._function)
        self.assertEqual(getlist.list_name, self._list_name)
        self.assertEqual(getlist.item_id, self._item_id)
        self.assertEqual(getlist.ipbx_id, self._ipbx_id)

    def test_handler_registration(self):
        connection = Mock(CTI)
        cti_handler = CTICommandHandler(connection)

        self.assertEqual(len(cti_handler._commands_to_run), 0)

        cti_handler.parse_message(self._dict_msg)

        self.assertTrue(len(cti_handler._commands_to_run) > 0)

        found = False
        for command in cti_handler._commands_to_run:
            if isinstance(command, GetList) and command.commandid == self._commandid:
                found = True

        self.assertTrue(found)
