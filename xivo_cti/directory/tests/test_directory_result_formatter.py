# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.directory import formatter


class TestDirectoryResultFormatter(unittest.TestCase):

    def test_format_directory_result(self):
        headers = [u'Name', u'Number', u'Number', u'Number']
        types = [u'name', u'number_office', u'number_mobile', u'number_on_the_road']
        results = [u'Dave ;4185555555;7893;98734;543']

        formatted_result = formatter.DirectoryResultFormatter.format(headers, types, results)

        expected_result = [
            {u'name': u'Dave',
             u'number': u'4185555555',
             u'number_type': formatter.DirectoryFieldType.office},
            {u'name': u'Dave',
             u'number': u'7893',
             u'number_type': formatter.DirectoryFieldType.mobile},
            {u'name': u'Dave',
             u'number': u'98734',
             u'number_type': formatter.DirectoryFieldType.other},
        ]

        self.assertEqual(sorted(formatted_result), sorted(expected_result))

    def test_format_directory_result_no_office_number(self):
        headers = [u'Name']
        types = [u'name']
        results = [u'Dave ']

        formatted_result = formatter.DirectoryResultFormatter.format(headers, types, results)

        expected_result = []

        self.assertEqual(formatted_result, expected_result)

    def test_format_directory_result_extra_fields(self):
        headers = [u'Name', u'Email', u'Number', u'Number', u'Number']
        types = [u'name', u'', u'number_office', u'number_mobile', u'number_on_the_road']
        results = [u'Dave ;dave@dave.com;4185555555;7893;98734;543']

        formatted_result = formatter.DirectoryResultFormatter.format(headers, types, results)

        expected_result = [
            {u'name': u'Dave',
             u'Email': u'dave@dave.com',
             u'number': u'4185555555',
             'number_type': formatter.DirectoryFieldType.office},
            {u'name': u'Dave',
             u'Email': u'dave@dave.com',
             u'number': u'7893',
             'number_type': formatter.DirectoryFieldType.mobile},
            {u'name': u'Dave',
             u'Email': u'dave@dave.com',
             u'number': u'98734',
             u'number_type': formatter.DirectoryFieldType.other},
        ]

        self.assertEqual(sorted(formatted_result), sorted(expected_result))

    def test_format_directory_result_empty_name(self):
        headers = [u'Name', u'Number']
        types = [u'name', u'number_office']
        results = [u' ;4185555555']

        formatted_result = formatter.DirectoryResultFormatter.format(headers, types, results)

        expected_result = [
            {u'name': u'',
             u'number': u'4185555555',
             u'number_type': formatter.DirectoryFieldType.office}
        ]

        self.assertEqual(sorted(formatted_result), sorted(expected_result))

    def test_format_directory_result_no_name(self):
        headers = [u'Number']
        types = [u'number_mobile']
        results = [u'555']

        formatted_result = formatter.DirectoryResultFormatter.format(headers, types, results)

        expected_result = []

        self.assertEqual(formatted_result, expected_result)

    def test_format_directory_result_empty_number(self):
        headers = [u'Name', u'Email', u'Number', u'Number', u'Number']
        types = [u'name', u'', u'number_office', u'number_mobile', u'number_on_the_road']
        results = [u'Dave ;dave@dave.com;4185555555;;98734']

        formatted_result = formatter.DirectoryResultFormatter.format(headers, types, results)

        expected_result = [
            {u'name': u'Dave',
             u'Email': u'dave@dave.com',
             u'number': u'4185555555',
             u'number_type': formatter.DirectoryFieldType.office},
            {u'name': u'Dave',
             u'Email': u'dave@dave.com',
             u'number': u'98734',
             u'number_type': formatter.DirectoryFieldType.other},
        ]

        self.assertEqual(sorted(formatted_result), sorted(expected_result))
