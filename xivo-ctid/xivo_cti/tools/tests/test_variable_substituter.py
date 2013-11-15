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

from hamcrest import assert_that, equal_to
from mock import Mock, mock_open, patch
from unittest import TestCase

from .. import variable_substituter as substituter


class TestVariableSubstituter(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_substitute_empty_string(self):
        string_containing_variables = ''
        variables = {}

        result = substituter.substitute(string_containing_variables,
                                        variables)

        assert_that(result, equal_to(string_containing_variables))

    def test_substitute_without_variables(self):
        string_containing_variables = 'abcdef()[]'
        variables = {}

        result = substituter.substitute(string_containing_variables,
                                        variables)

        assert_that(result, equal_to(string_containing_variables))

    def test_substitute_with_unknown_variable(self):
        string_containing_variables = '{abcdef}'
        variables = {}

        result = substituter.substitute(string_containing_variables,
                                        variables)

        assert_that(result, equal_to(string_containing_variables))

    def test_substitute_with_known_variable(self):
        string_containing_variables = '{variable}'
        variables = {'variable': 'value'}

        result = substituter.substitute(string_containing_variables,
                                        variables)

        assert_that(result, equal_to('value'))

    def test_substitute_with_known_variable_and_text_around(self):
        string_containing_variables = 'abc {variable} def'
        variables = {'variable': 'value'}

        result = substituter.substitute(string_containing_variables,
                                        variables)

        assert_that(result, equal_to('abc value def'))

    @patch('base64.b64encode')
    def test_substitute_picture(self, base64):
        file_content = Mock()
        mock_urllib2 = mock_open(read_data=file_content)
        with patch('urllib2.urlopen', mock_urllib2, create=True) as urllib2:
            base64_string = base64.return_value = 'abcdef'

            string_containing_variables = '{xivo-callerpicture}'
            variables = {'xivo-userid': '12'}

            result = substituter.substitute(string_containing_variables,
                                            variables)

            assert_that(result, equal_to(base64_string))
            urllib2.assert_called_once_with(substituter.USER_PICTURE_URL % '12')
            base64.assert_called_once_with(file_content)
