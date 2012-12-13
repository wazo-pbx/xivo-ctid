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
# contracted with Avencall. See the LICENSE file at top of the source tree
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

from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.commands.getlist import GetList
from xivo_cti.cti.commands.getlists.update_config import UpdateConfig
from mock import Mock
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.cti.cti_command_handler import CTICommandHandler


class TestUpdateConfig(unittest.TestCase):

    _commandid = 1446226295
    _list_name = 'users'
    _item_id = '1'
    _ipbx_id = 'xivo'
    _msg_dict = {CTICommand.CLASS: GetList.COMMAND_CLASS,
                 CTICommand.COMMANDID: _commandid,
                 GetList.FUNCTION: UpdateConfig.FUNCTION_NAME,
                 GetList.LIST_NAME: _list_name,
                 GetList.ITEM_ID: _item_id,
                 GetList.IPBX_ID: _ipbx_id}

    def test_update_config(self):
        update_config = UpdateConfig()

        self.assertEqual(update_config.command_class, GetList.COMMAND_CLASS)
        self.assertEqual(update_config.function, UpdateConfig.FUNCTION_NAME)

    def test_from_dict(self):
        update_config = UpdateConfig.from_dict(self._msg_dict)

        self.assertEqual(update_config.command_class, GetList.COMMAND_CLASS)
        self.assertEqual(update_config.function, UpdateConfig.FUNCTION_NAME)
        self.assertEqual(update_config.commandid, self._commandid)
        self.assertEqual(update_config.list_name, self._list_name)
        self.assertEqual(update_config.item_id, self._item_id)
        self.assertEqual(update_config.ipbx_id, self._ipbx_id)

    def test_handler_registration(self):
        connection = Mock(CTI)
        cti_handler = CTICommandHandler(connection)

        self.assertEqual(len(cti_handler._commands_to_run), 0)

        cti_handler.parse_message(self._msg_dict)

        self.assertTrue(len(cti_handler._commands_to_run) > 0)

        found = False
        for command in cti_handler._commands_to_run:
            if isinstance(command, UpdateConfig) and command.commandid == self._commandid:
                found = True

        self.assertTrue(found)

    def test_get_reply_item(self):
        update_config = UpdateConfig.from_dict(self._msg_dict)
        item = {'field': 'value'}
        ret = update_config.get_reply_item(item)

        self.assertTrue(CTICommand.CLASS in ret and ret[CTICommand.CLASS] == GetList.COMMAND_CLASS)
        self.assertTrue(UpdateConfig.CONFIG in ret and ret[UpdateConfig.CONFIG] == item)
        self.assertTrue(UpdateConfig.FUNCTION in ret and ret[UpdateConfig.FUNCTION] == UpdateConfig.FUNCTION_NAME)
        self.assertTrue(GetList.LIST_NAME in ret and ret[GetList.LIST_NAME] == self._list_name)
        self.assertTrue(CTICommand.REPLYID in ret and ret[CTICommand.REPLYID] == self._commandid)
        self.assertTrue(GetList.ITEM_ID in ret and ret[GetList.ITEM_ID] == self._item_id)
        self.assertTrue(GetList.IPBX_ID in ret and ret[GetList.IPBX_ID] == self._ipbx_id)
