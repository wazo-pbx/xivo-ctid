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

from xivo_cti.cti.commands.getlists.list_id import ListID
from xivo_cti.cti.commands.getlist import GetList
from xivo_cti.cti.cti_command import CTICommand
from mock import Mock
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.cti.cti_command_handler import CTICommandHandler
from xivo_cti.tools.weak_method import WeakMethodFree


class TestListID(unittest.TestCase):

    _commandid = 1446226295
    _list_name = 'users'
    _item_id = '1'
    _ipbx_id = 'xivo'
    _msg_dict = {CTICommand.CLASS: GetList.COMMAND_CLASS,
                 CTICommand.COMMANDID: _commandid,
                 GetList.FUNCTION: ListID.FUNCTION_NAME,
                 GetList.LIST_NAME: _list_name,
                 GetList.ITEM_ID: _item_id,
                 GetList.IPBX_ID: _ipbx_id}

    def test_list_id(self):
        list_id = ListID()

        self.assertEqual(list_id.command_class, GetList.COMMAND_CLASS)
        self.assertEqual(list_id.function, ListID.FUNCTION_NAME)

    def test_from_dict(self):
        list_id = ListID.from_dict(self._msg_dict)

        self.assertTrue(isinstance(list_id, ListID))
        self.assertEqual(list_id.command_class, ListID.COMMAND_CLASS)
        self.assertEqual(list_id.commandid, self._commandid)
        self.assertEqual(list_id.function, ListID.FUNCTION_NAME)
        self.assertEqual(list_id.list_name, self._list_name)
        self.assertEqual(list_id.item_id, self._item_id)
        self.assertEqual(list_id.ipbx_id, self._ipbx_id)

    def test_handler_registration(self):
        connection = Mock(CTI)
        cti_handler = CTICommandHandler(connection)

        self.assertEqual(len(cti_handler._commands_to_run), 0)

        cti_handler.parse_message(self._msg_dict)

        self.assertTrue(len(cti_handler._commands_to_run) > 0)

        found = False
        for command in cti_handler._commands_to_run:
            if isinstance(command, ListID) and command.commandid == self._commandid:
                found = True

        self.assertTrue(found)

    def test_get_reply_list(self):
        list_id = ListID.from_dict(self._msg_dict)
        replied_list = ['1', '2', '7']

        ret = list_id.get_reply_list(replied_list)

        self.assertTrue(CTICommand.CLASS in ret and ret[CTICommand.CLASS] == GetList.COMMAND_CLASS)
        self.assertTrue(GetList.FUNCTION in ret and ret[GetList.FUNCTION] == ListID.FUNCTION_NAME)
        self.assertTrue('list' in ret and ret['list'] == replied_list)
        self.assertTrue(GetList.LIST_NAME in ret and ret[GetList.LIST_NAME] == self._list_name)
        self.assertTrue('replyid' in ret and ret['replyid'] == self._commandid)
        self.assertTrue(GetList.IPBX_ID in ret and ret[GetList.IPBX_ID] == self._ipbx_id)

    def test_get_callbacks(self):
        def func1(param):
            pass

        def func2(param):
            pass

        GetList.register_callback(func1)
        ListID.register_callback(func2)

        list_id = ListID.from_dict(self._msg_dict)

        callbacks = list_id.callbacks()

        self.assertEqual(len(callbacks), 1)
        self.assertEqual(WeakMethodFree(func2), callbacks[0])
