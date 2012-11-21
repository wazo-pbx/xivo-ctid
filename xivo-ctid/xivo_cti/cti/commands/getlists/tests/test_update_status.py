# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from xivo_cti.cti.commands.getlists.update_status import UpdateStatus
from xivo_cti.cti.commands.getlist import GetList
from xivo_cti.cti.cti_command import CTICommand
from mock import Mock
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.cti.cti_command_handler import CTICommandHandler


class TestUpdateStatus(unittest.TestCase):

    _commandid = 1446226295
    _list_name = 'users'
    _item_id = '1'
    _ipbx_id = 'xivo'
    _msg_dict = {CTICommand.CLASS: GetList.COMMAND_CLASS,
                 CTICommand.COMMANDID: _commandid,
                 GetList.FUNCTION: UpdateStatus.FUNCTION_NAME,
                 GetList.LIST_NAME: _list_name,
                 GetList.ITEM_ID: _item_id,
                 GetList.IPBX_ID: _ipbx_id}

    def test_update_status(self):
        update_status = UpdateStatus()
        self.assertEqual(update_status.command_class, GetList.COMMAND_CLASS)
        self.assertEqual(update_status.function, UpdateStatus.FUNCTION_NAME)

    def test_from_dict(self):
        update_status = UpdateStatus.from_dict(self._msg_dict)

        self.assertEqual(update_status.commandid, self._commandid)
        self.assertEqual(update_status.command_class, GetList.COMMAND_CLASS)
        self.assertEqual(update_status.function, UpdateStatus.FUNCTION_NAME)
        self.assertEqual(update_status.list_name, self._list_name)
        self.assertEqual(update_status.item_id, self._item_id)
        self.assertEqual(update_status.ipbx_id, self._ipbx_id)

    def test_get_reply_item(self):
        update_status = UpdateStatus.from_dict(self._msg_dict)
        item_list = {'key': 'value'}

        reply = update_status.get_reply_item(item_list)

        self.assertTrue(CTICommand.CLASS in reply and reply[CTICommand.CLASS] == GetList.COMMAND_CLASS)
        self.assertTrue(GetList.FUNCTION in reply and reply[GetList.FUNCTION] == UpdateStatus.FUNCTION_NAME)
        self.assertTrue(GetList.LIST_NAME in reply and reply[GetList.LIST_NAME] == self._list_name)
        self.assertTrue(CTICommand.REPLYID in reply and reply[CTICommand.REPLYID] == self._commandid)
        self.assertTrue(UpdateStatus.STATUS in reply and reply[UpdateStatus.STATUS] == item_list)
        self.assertTrue(GetList.ITEM_ID in reply and reply[GetList.ITEM_ID] == self._item_id)
        self.assertTrue(GetList.IPBX_ID in reply and reply[GetList.IPBX_ID] == self._ipbx_id)

    def test_handler_registration(self):
        connection = Mock(CTI)
        cti_handler = CTICommandHandler(connection)

        self.assertEqual(len(cti_handler._commands_to_run), 0)

        cti_handler.parse_message(self._msg_dict)

        self.assertTrue(len(cti_handler._commands_to_run) > 0)

        found = False
        for command in cti_handler._commands_to_run:
            if isinstance(command, UpdateStatus) and command.commandid == self._commandid:
                found = True

        self.assertTrue(found)
