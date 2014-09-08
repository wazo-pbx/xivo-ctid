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

from mock import Mock, patch
from hamcrest import assert_that
from hamcrest import equal_to

from xivo_cti.cti_anylist import ContextAwareAnyList
from xivo_cti.ioc.context import context as cti_context


class ConcreteContextAwareAnyList(ContextAwareAnyList):

    def __init__(self):
        self._innerdata = Mock()
        super(ConcreteContextAwareAnyList, self).__init__('')
        self.add_notifier = Mock()
        self.edit_notifier = Mock()
        self.get_contexts = Mock()


class TestContextAwareAnyList(unittest.TestCase):

    item_id = '1'
    keeplist = {
        item_id: {
            'context': 'foobar'
        }
    }
    item_ids_by_context = {
        'foobar': [item_id]
    }

    def setUp(self):
        self.listname_obj = Mock()
        self.list = ConcreteContextAwareAnyList()
        self.list.listname_obj = self.listname_obj

    def test_init_data_builds_item_ids_by_context(self):
        self.listname_obj.get_list.return_value = self.keeplist

        self.list.init_data()

        assert_that(self.list._item_ids_by_context, equal_to(self.item_ids_by_context))

    @patch('xivo_cti.cti_anylist.AnyList.add')
    def test_add_update_item_ids_by_context(self, mock_anylist_add):
        self.listname_obj.get_list.return_value = self.keeplist

        self.list.init_data()
        self.list.add(self.item_id)

        assert_that(self.list._item_ids_by_context, equal_to(self.item_ids_by_context))
        mock_anylist_add.assert_called_once_with(self.item_id)

    @patch('xivo_cti.cti_anylist.AnyList.add')
    def test_add_update_item_ids_by_context_twice(self, mock_anylist_add):
        self.listname_obj.get_list.return_value = self.keeplist

        self.list.init_data()
        self.list.add(self.item_id)
        self.list.add(self.item_id)

        assert_that(self.list._item_ids_by_context, equal_to(self.item_ids_by_context))
        mock_anylist_add.count_calls = 2
        mock_anylist_add.assert_called_with(self.item_id)

    @patch('xivo_cti.cti_anylist.AnyList.delete')
    def test_remove_update_item_ids_by_context(self, mock_anylist_delete):
        self.listname_obj.get_list.return_value = self.keeplist

        self.list.init_data()
        self.list.delete(self.item_id)

        assert_that(self.list._item_ids_by_context, equal_to({}))
        mock_anylist_delete.assert_called_once_with(self.item_id)

    def test_given_no_context_separation_when_send_message_then_send_cti_event(self):
        self.listname_obj.get_list.return_value = self.keeplist
        self.list._ctiserver = Mock()
        cti_config = Mock()
        cti_config.return_value.part_context.return_value = False
        cti_context.reset()
        cti_context.register('cti_config', cti_config)

        message_id = 3
        message = {
            'class': 'getlist',
            'listname': 'test-list',
            'function': 'addconfig',
            'tipbxid': 1,
            'list': [message_id]
        }

        self.list.init_data()
        self.list._send_message(message, message_id)

        self.list._ctiserver.send_cti_event.assert_called_once_with(message)

    def test_given_users_listname_when_send_message_then_get_contexts(self):
        self.listname_obj.get_list.return_value = self.keeplist
        self.list._ctiserver = Mock()
        mock_connection = Mock()
        self.list._ctiserver.get_connected.return_value = [mock_connection]
        context = 'testing'
        self.list.get_contexts.return_value = context
        cti_config = Mock()
        cti_config.return_value.part_context.return_value = True
        cti_context.reset()
        cti_context.register('cti_config', cti_config)

        message_id = 3
        message = {
            'class': 'getlist',
            'listname': 'users',
            'function': 'addconfig',
            'tipbxid': 1,
            'list': [message_id]
        }
        self.list.listname = 'users'

        self.list.init_data()
        self.list._send_message(message, message_id)


        self.list.get_contexts.assert_called_once_with(message_id)
        self.list._ctiserver.get_connected.assert_called_once_with({'contexts': context})
        mock_connection.append_msg.assert_called_once_with(message)
