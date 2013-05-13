# -*- coding: utf-8 -*-

# Copyright (C) 2013  Avencall
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
from xivo_cti.cti_anylist import ContextAwareAnyList

from mock import Mock

from hamcrest import assert_that
from hamcrest import equal_to


class ConcreteContextAwareAnyList(ContextAwareAnyList):

    def __init__(self):
        self._innerdata = Mock()
        super(ConcreteContextAwareAnyList, self).__init__('')
        self.add_notifier = Mock()
        self.edit_notifier = Mock()


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

    def test_add_update_item_ids_by_context(self):
        self.listname_obj.get_list.return_value = {}
        self.listname_obj.get.return_value = self.keeplist

        self.list.init_data()
        self.list.add(self.item_id)

        assert_that(self.list._item_ids_by_context, equal_to(self.item_ids_by_context))

    def test_add_update_item_ids_by_context_twice(self):
        self.listname_obj.get_list.return_value = {}
        self.listname_obj.get.return_value = self.keeplist

        self.list.init_data()
        self.list.add(self.item_id)
        self.list.add(self.item_id)

        assert_that(self.list._item_ids_by_context, equal_to(self.item_ids_by_context))

    def test_remove_update_item_ids_by_context(self):
        self.listname_obj.get_list.return_value = self.keeplist

        self.list.init_data()
        self.list.delete(self.item_id)

        assert_that(self.list._item_ids_by_context, equal_to({}))
