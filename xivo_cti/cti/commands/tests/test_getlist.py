# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
