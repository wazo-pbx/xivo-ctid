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
from mock import Mock
from xivo_cti.cti import cti_command_registry


class TestRegistry(unittest.TestCase):

    def setUp(self):
        self._old_classes_by_class_name = cti_command_registry._classes_by_class_name
        self._old_getlist_classes_by_fun_name = cti_command_registry._getlist_classes_by_fun_name
        cti_command_registry._classes_by_class_name = {}
        cti_command_registry._getlist_classes_by_fun_name = {}

    def tearDown(self):
        cti_command_registry._classes_by_class_name = self._old_classes_by_class_name
        cti_command_registry._getlist_classes_by_fun_name = self._old_getlist_classes_by_fun_name

    def test_get_class_with_registered_class_that_match(self):
        klass = self._new_class('foo')
        klass.match_message.return_value = True
        msg = self._new_msg('foo')

        cti_command_registry.register_class(klass)

        result = cti_command_registry.get_class(msg)

        klass.match_message.assert_called_once_with(msg)
        self.assertEqual(result, [klass])

    def test_get_class_with_registered_class_that_doesnt_match(self):
        klass = self._new_class('foo')
        klass.match_message.return_value = False
        msg = self._new_msg('foo')

        cti_command_registry.register_class(klass)

        result = cti_command_registry.get_class(msg)

        klass.match_message.assert_called_once_with(msg)
        self.assertEqual(result, [])

    def test_get_class_with_unregistered_class(self):
        msg = self._new_msg('foo')

        result = cti_command_registry.get_class(msg)

        self.assertEqual(result, [])

    def test_get_class_with_two_registered_class(self):
        klass1 = self._new_class('foo')
        klass2 = self._new_class('foo')
        msg = self._new_msg('foo')

        cti_command_registry.register_class(klass1)
        cti_command_registry.register_class(klass2)

        result = cti_command_registry.get_class(msg)

        self.assertEqual(sorted(result), sorted([klass1, klass2]))

    def test_register_class_with_getlist_raise_error(self):
        klass = self._new_class('getlist')

        self.assertRaises(Exception, cti_command_registry.register_class, klass)

    def test_get_class_with_registered_getlist_class(self):
        function = 'updateconfig'
        klass = self._new_class('getlist')
        msg = self._new_msg('getlist')
        msg['function'] = function

        cti_command_registry.register_getlist_class(klass, function)

        result = cti_command_registry.get_class(msg)

        self.assertEqual(result, [klass])

    def test_register_two_getlist_classes_raise_error(self):
        function = 'updateconfig'
        klass1 = self._new_class('getlist')
        klass2 = self._new_class('getlist')

        cti_command_registry.register_getlist_class(klass1, function)
        self.assertRaises(Exception, cti_command_registry.register_getlist_class, klass2, function)

    def _new_class(self, class_name):
        klass = Mock()
        klass.class_name = class_name
        return klass

    def _new_msg(self, class_name):
        return {'class': class_name}
