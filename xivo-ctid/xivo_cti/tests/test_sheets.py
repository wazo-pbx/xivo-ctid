# -*- coding: UTF-8 -*-

import unittest

from mock import Mock
from xivo_cti import cti_sheets
from xivo_cti.innerdata import Channel


class TestSheets(unittest.TestCase):

    def setUp(self):
        self.title = 'My Test Sheet Title'
        self.field_type = 'text'
        self.default_value = 'my_default_value'
        self.format_string = '{xivo-test}'
        self.disabled = 0

        self.line_properties = [self.title,
                                self.field_type,
                                self.default_value,
                                self.format_string,
                                self.disabled]

        self.sheet = cti_sheets.Sheet(None, None, None)
        self.sheet.channelprops = Mock(Channel)

    def test_resolv_line_content_no_substitution_with_default(self):
        data = {}
        default_value = 'bar'
        display_value = 'foobar'
        expected = display_value

        result = self._substitute_via_resolv_line_content(data, default_value, display_value)

        self.assertEqual(expected, result)

    def test_resolv_line_content_no_substitution_with_no_default(self):
        data = {}
        default_value = ''
        display_value = 'foobar'
        expected = display_value

        result = self._substitute_via_resolv_line_content(data, default_value, display_value)

        self.assertEqual(expected, result)

    def test_resolv_line_content_with_simple_and_present_substitution(self):
        data = {'xivo': {'test': 'foobar'}}
        default_value = ''
        display_value = '{xivo-test}'
        expected = data['xivo']['test']

        result = self._substitute_via_resolv_line_content(data, default_value, display_value)

        self.assertEqual(expected, result)

    def test_resolv_line_content_with_simple_and_missing_substitution_with_default(self):
        data = {}
        default_value = 'bar'
        display_value = '{xivo-test}'
        expected = default_value

        result = self._substitute_via_resolv_line_content(data, default_value, display_value)

        self.assertEqual(expected, result)

    def test_resolv_line_content_with_simple_and_missing_substitution_with_no_default(self):
        data = {}
        default_value = ''
        display_value = '{xivo-test}'
        expected = display_value

        result = self._substitute_via_resolv_line_content(data, default_value, display_value)

        self.assertEqual(expected, result)

    def test_resolv_line_content_with_complex_and_present_substitution(self):
        data = {'xivo': {'test': 'foobar'}}
        default_value = ''
        display_value = 'A {xivo-test}.'
        expected = 'A foobar.'

        result = self._substitute_via_resolv_line_content(data, default_value, display_value)

        self.assertEqual(expected, result)

    def test_resolv_line_content_with_complex_and_missing_substitution_with_default(self):
        data = {}
        default_value = 'bar'
        display_value = 'A {xivo-test}.'
        expected = default_value

        result = self._substitute_via_resolv_line_content(data, default_value, display_value)

        self.assertEqual(expected, result)

    def test_resolv_line_content_with_complex_and_missing_substitution_with_no_default(self):
        data = {}
        default_value = ''
        display_value = 'A {xivo-test}.'
        expected = display_value

        result = self._substitute_via_resolv_line_content(data, default_value, display_value)

        self.assertEqual(expected, result)

    def test_resolv_line_content_with_multiple_substitutions(self):
        data = {'xivo': {'test1': 'foo', 'test2': 'bar'}}
        default_value = ''
        display_value = 'A {xivo-test1} and {xivo-test2}.'
        expected = 'A foo and bar.'

        result = self._substitute_via_resolv_line_content(data, default_value, display_value)

        self.assertEqual(expected, result)

    def test_resolv_line_content_with_multiple_substitutions_and_one_missing(self):
        data = {'xivo': {'test1': 'foo'}}
        default_value = ''
        display_value = 'A {xivo-test1} and {xivo-test2}.'
        expected = 'A foo and .'

        result = self._substitute_via_resolv_line_content(data, default_value, display_value)

        self.assertEqual(expected, result)

    def test_resolv_line_content_with_multiple_substitutions_and_all_missing_and_default(self):
        data = {}
        default_value = 'bar'
        display_value = 'A {xivo-test1} and {xivo-test2}.'
        expected = default_value

        result = self._substitute_via_resolv_line_content(data, default_value, display_value)

        self.assertEqual(expected, result)

    def test_resolv_line_content_with_multiple_substitutions_and_all_missing_and_no_default(self):
        data = {}
        default_value = ''
        display_value = 'A {xivo-test1} and {xivo-test2}.'
        expected = display_value

        result = self._substitute_via_resolv_line_content(data, default_value, display_value)

        self.assertEqual(expected, result)

    def _substitute_via_resolv_line_content(self, data, default_value, display_value):
        self.sheet.channelprops.extra_data = data

        result = self.sheet.resolv_line_content(('title', 'ftype', default_value, display_value))

        return result['contents']

    def test_resolv_line_content_callerpicture(self):
        user_id = '6'
        encoded_picture = 'my picture base 64 encoding'
        self.sheet.channelprops.extra_data = {'xivo': {'userid': user_id}}
        self.sheet._get_user_picture = Mock(return_value=encoded_picture)
        expected = {'name': self.title,
                    'type': self.field_type,
                    'contents': encoded_picture}

        result = self.sheet.resolv_line_content([self.title,
                                                 self.field_type,
                                                 self.default_value,
                                                 '{xivo-callerpicture}'])
        self.sheet._get_user_picture.assert_called_once_with(user_id)

        self.assertEqual(result, expected)
