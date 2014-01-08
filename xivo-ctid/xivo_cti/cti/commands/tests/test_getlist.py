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
from xivo_cti.cti import cti_command_registry
from xivo_cti.cti.commands.getlist import ListID, UpdateConfig, UpdateStatus


class TestGetlist(unittest.TestCase):

    _list_name = 'users'
    _item_id = '1'

    _listid_msg = {
        'class': 'getlist',
        'function': 'listid',
        'listname': _list_name,
    }
    _updateconfig_msg = {
        'class': 'getlist',
        'function': 'updateconfig',
        'listname': _list_name,
        'tid': _item_id,
    }
    _updatestatus_msg = {
        'class': 'getlist',
        'function': 'updatestatus',
        'listname': _list_name,
        'tid': _item_id,
    }

    def test_list_id_msg(self):
        command = ListID.from_dict(self._listid_msg)

        self.assertEqual(command.list_name, self._list_name)

    def test_list_id_registration(self):
        klass = cti_command_registry.get_class(self._listid_msg)

        self.assertEqual(klass, [ListID])

    def test_update_config_msg(self):
        command = UpdateConfig.from_dict(self._updateconfig_msg)

        self.assertEqual(command.list_name, self._list_name)
        self.assertEqual(command.item_id, self._item_id)

    def test_update_config_registration(self):
        klass = cti_command_registry.get_class(self._updateconfig_msg)

        self.assertEqual(klass, [UpdateConfig])

    def test_update_status_msg(self):
        command = UpdateStatus.from_dict(self._updatestatus_msg)

        self.assertEqual(command.list_name, self._list_name)
        self.assertEqual(command.item_id, self._item_id)

    def test_update_status_registration(self):
        klass = cti_command_registry.get_class(self._updatestatus_msg)

        self.assertEqual(klass, [UpdateStatus])
