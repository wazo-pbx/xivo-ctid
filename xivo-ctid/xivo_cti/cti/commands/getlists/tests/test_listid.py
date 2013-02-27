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

from xivo_cti.cti.commands.getlists.list_id import ListID
from xivo_cti.cti.commands.getlist import GetList
from mock import Mock
from xivo_cti.cti.cti_command_handler import CTICommandHandler
from xivo_cti.tools.weak_method import WeakMethodFree


class TestListID(unittest.TestCase):

    _commandid = 1446226295
    _list_name = 'users'
    _ipbx_id = 'xivo'
    _msg_dict = {'class': GetList.class_name,
                 'commandid': _commandid,
                 'function': ListID.function_name,
                 'listname': _list_name}

    def test_from_dict(self):
        list_id = ListID.from_dict(self._msg_dict)

        self.assertEqual(list_id.list_name, self._list_name)

    def test_handler_registration(self):
        connection = Mock()
        cti_handler = CTICommandHandler(connection)

        self.assertEqual(len(cti_handler._commands_to_run), 0)

        cti_handler.parse_message(self._msg_dict)

        self.assertTrue(len(cti_handler._commands_to_run) > 0)

        found = False
        for command in cti_handler._commands_to_run:
            if command.commandid == self._commandid:
                found = True

        self.assertTrue(found)

    def test_get_callbacks(self):
        def func1(param):
            pass

        def func2(param):
            pass

        ListID.register_callback_params(func2)

        list_id = ListID.from_dict(self._msg_dict)

        callbacks = list_id.callbacks_with_params()

        self.assertEqual(len(callbacks), 1)
        self.assertEqual(WeakMethodFree(func2), callbacks[0][0])
