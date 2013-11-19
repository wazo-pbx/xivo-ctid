# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from hamcrest import assert_that, has_length, has_entries
from mock import Mock, patch, sentinel
from xivo_cti import cti_sheets


class TestSheets(unittest.TestCase):

    def setUp(self):
        self.title = 'My Test Sheet Title'
        self.field_type = 'text'
        self.default_value = 'my_default_value'
        self.sheet = cti_sheets.Sheet(None, None, sentinel.uid)

    @patch('xivo_cti.tools.variable_substituter.substitute_with_default')
    def test_resolv_line_content(self, substitute):
        value_with_variables = 'a string with {variable}'
        variable_values = {'variable': 'value'}
        self.sheet.variable_values = Mock(return_value=variable_values)
        value_substituted = substitute.return_value = 'a string with value'

        result = self.sheet.resolv_line_content([self.title,
                                                 self.field_type,
                                                 self.default_value,
                                                 value_with_variables])

        substitute.assert_called_once_with(value_with_variables, self.default_value, variable_values)
        assert_that(result, has_length(3))
        assert_that(result, has_entries({'name': self.title,
                                         'type': self.field_type,
                                         'contents': value_substituted}))

    @patch('xivo_cti.ioc.context.context.get')
    def test_variable_values_empty(self, context):
        variable_aggregator = context.return_value
        variable_aggregator.get.return_value = {}

        result = self.sheet.variable_values()

        assert_that(result, has_length(0))
        variable_aggregator.get.assert_called_once_with(sentinel.uid)

    @patch('xivo_cti.ioc.context.context.get')
    def test_variable_values_with_xivo_variables(self, context):
        variable_aggregator = context.return_value
        variable_aggregator.get.return_value = {'xivo': {'variable1': 'value1',
                                                         'variable2': 'value2'}}

        result = self.sheet.variable_values()

        assert_that(result, has_length(2))
        assert_that(result, has_entries({'xivo-variable1': 'value1',
                                         'xivo-variable2': 'value2'}))
        variable_aggregator.get.assert_called_once_with(sentinel.uid)

    @patch('xivo_cti.ioc.context.context.get')
    def test_variable_values_with_two_variable_types(self, context):
        variable_aggregator = context.return_value
        variable_aggregator.get.return_value = {'xivo': {'variable1': 'value1',
                                                         'variable2': 'value2'},
                                                'db': {'variable3': 'value3',
                                                       'variable4': 'value4'}}

        result = self.sheet.variable_values()

        assert_that(result, has_length(4))
        assert_that(result, has_entries({'xivo-variable1': 'value1',
                                         'xivo-variable2': 'value2',
                                         'db-variable3': 'value3',
                                         'db-variable4': 'value4'}))
        variable_aggregator.get.assert_called_once_with(sentinel.uid)
