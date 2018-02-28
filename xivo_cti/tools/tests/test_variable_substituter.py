# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import urllib2

from hamcrest import assert_that, equal_to
from mock import Mock, mock_open, patch
from unittest import TestCase

from .. import variable_substituter as substituter


class TestVariableSubstituter(TestCase):

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

    @patch('urllib2.urlopen', new_callable=mock_open, read_data='picture_content')
    @patch('base64.b64encode')
    def test_substitute_picture(self, base64, urlopen):
        base64_string = base64.return_value = 'abcdef'
        string_containing_variables = '{xivo-callerpicture}'
        variables = {'xivo-userid': '12'}

        result = substituter.substitute(string_containing_variables,
                                        variables)

        assert_that(result, equal_to(base64_string))
        urlopen.assert_called_once_with(substituter.USER_PICTURE_URL % '12')
        base64.assert_called_once_with('picture_content')

    @patch('urllib2.urlopen', Mock(side_effect=urllib2.HTTPError('', 404, 'Not found', None, None)))
    def test_substitute_picture_invalid_http_request(self):
        string_containing_variables = '{xivo-callerpicture}'
        variables = {'xivo-userid': '12'}

        substituter.substitute(string_containing_variables, variables)
        # No exception

    def test_substitute_with_default_with_empty_string(self):
        string_containing_variables = ''
        default_value = 'default'
        variables = {}

        result = substituter.substitute_with_default(string_containing_variables,
                                                     default_value,
                                                     variables)

        assert_that(result, equal_to(string_containing_variables))

    def test_substitute_with_default_with_default_without_variables(self):
        string_containing_variables = 'abcdef()[]'
        default_value = 'default'
        variables = {}

        result = substituter.substitute_with_default(string_containing_variables,
                                                     default_value,
                                                     variables)

        assert_that(result, equal_to(string_containing_variables))

    def test_substitute_with_default_with_default_with_unknown_variable(self):
        string_containing_variables = '{abcdef}'
        default_value = 'default'
        variables = {}

        result = substituter.substitute_with_default(string_containing_variables,
                                                     default_value,
                                                     variables)

        assert_that(result, equal_to(default_value))

    def test_substitute_with_default_with_default_with_multiple_unknown_variable(self):
        string_containing_variables = '{abc} def {ghi}'
        default_value = 'default'
        variables = {}

        result = substituter.substitute_with_default(string_containing_variables,
                                                     default_value,
                                                     variables)

        assert_that(result, equal_to(default_value))

    def test_substitute_with_default_with_default_with_variable_value_none(self):
        string_containing_variables = '{variable}'
        default_value = 'default'
        variables = {'variable': None}

        result = substituter.substitute_with_default(string_containing_variables,
                                                     default_value,
                                                     variables)

        assert_that(result, equal_to(default_value))

    def test_substitute_with_default_with_default_with_known_variable(self):
        string_containing_variables = '{variable}'
        default_value = 'default'
        variables = {'variable': 'value'}

        result = substituter.substitute_with_default(string_containing_variables,
                                                     default_value,
                                                     variables)

        assert_that(result, equal_to('value'))

    def test_substitute_with_default_with_default_with_known_variable_and_text_around(self):
        string_containing_variables = 'abc {variable} def'
        default_value = 'default'
        variables = {'variable': 'value'}

        result = substituter.substitute_with_default(string_containing_variables,
                                                     default_value,
                                                     variables)

        assert_that(result, equal_to('abc value def'))

    def test_substitute_with_default_with_default_with_multiple_known_variable(self):
        string_containing_variables = 'abc {variable1} def {variable2} ghi'
        default_value = 'default'
        variables = {'variable1': 'value1',
                     'variable2': 'value2'}

        result = substituter.substitute_with_default(string_containing_variables,
                                                     default_value,
                                                     variables)

        assert_that(result, equal_to('abc value1 def value2 ghi'))

    def test_substitute_with_default_with_default_with_multiple_variable_one_unknown(self):
        string_containing_variables = 'abc {variable1} def {variable2} ghi'
        default_value = 'default'
        variables = {'variable1': 'value1'}

        result = substituter.substitute_with_default(string_containing_variables,
                                                     default_value,
                                                     variables)

        assert_that(result, equal_to('abc value1 def {variable2} ghi'))

    @patch('urllib2.urlopen', new_callable=mock_open, read_data='picture_content')
    @patch('base64.b64encode')
    def test_substitute_with_default_picture(self, base64, urlopen):
        base64_string = base64.return_value = 'abcdef'
        string_containing_variables = '{xivo-callerpicture}'
        variables = {'xivo-userid': '12'}

        result = substituter.substitute(string_containing_variables,
                                        variables)

        assert_that(result, equal_to(base64_string))
        urlopen.assert_called_once_with(substituter.USER_PICTURE_URL % '12')
        base64.assert_called_once_with('picture_content')
