# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import assert_that, contains, contains_inanyorder, empty

from ..old_directory_formatter import OldDirectoryFormatter


class TestOldDirectoryFormatter(unittest.TestCase):

    def setUp(self):
        self.formatter = OldDirectoryFormatter()

    def test_no_results(self):
        dird_result = {u'column_types': ['', 'phone', '', '', '', ''],
                       u'term': u'foobar',
                       u'column_headers': ['Nom', 'Numéro', 'Entreprise', 'E-mail', 'Source'],
                       u'results': []}

        headers, types, resultlist = self.formatter.format_results(dird_result)

        assert_that(headers, contains('Nom', 'Numéro', 'Entreprise', 'E-mail', 'Source'))
        assert_that(types, contains('', 'phone', '', '', '', ''))
        assert_that(resultlist, empty())

    def test_resultlist_with_results(self):
        dird_result = {
            u'column_types': [u'name', u'name', u'number', u'callable', u'favorite', u'personal'],
            u'term': u'o',
            u'column_headers': [u'Firstname', u'Lastname', u'Number', u'Mobile', u'Favorite', u'Personal'],
            u'results': [
                {u'source': u'xivo_users',
                 u'column_values': [u'Bob', None, u'1002', None, False, False],
                 u'relations': {u'xivo_id': u'1c48a8d9-b937-4ca2-aa0d-2a9af075b258',
                                u'user_id': 2,
                                u'source_entry_id': u'2',
                                u'endpoint_id': 2, u'agent_id': 1}},
                {u'source': u'my_phonebook',
                 u'column_values': [u'El', u'Diablo', u'4185555666', None, False, False],
                 u'relations': {u'xivo_id': None,
                                u'user_id': None,
                                u'source_entry_id': None,
                                u'endpoint_id': None,
                                u'agent_id': None}}]}

        _, _, resultlist = self.formatter.format_results(dird_result)

        assert_that(resultlist, contains_inanyorder(u'Bob;;1002;',
                                                    u'El;Diablo;4185555666;'))

    def test_that_dird_specific_columns_are_not_included(self):
        dird_result = {
            u'column_types': [u'name', u'name', u'number', u'callable', u'favorite', u'personal'],
            u'term': u'o',
            u'column_headers': [u'Firstname', u'Lastname', u'Number', u'Mobile', u'Favorite', u'Personal'],
            u'results': [],
        }

        headers, types_, _ = self.formatter.format_results(dird_result)

        assert_that(types_, contains('name', 'name', 'number', 'callable'))
        assert_that(headers, contains('Firstname', 'Lastname', 'Number', 'Mobile'))

    def test_format_headers(self):
        dird_result = {"column_types": ["name",
                                        "name",
                                        "number_office",
                                        "callable",
                                        "favorite",
                                        "personal"],
                       "column_headers": ["Firstname",
                                          "Lastname",
                                          "Number",
                                          "Mobile",
                                          "Favorite",
                                          "Personal"]}

        headers = self.formatter.format_headers(dird_result)

        assert_that(headers, contains(('Firstname', 'name'),
                                      ('Lastname', 'name'),
                                      ('Number', 'number'),
                                      ('Mobile', 'callable')))

    def test_that_multiple_numbers_return_one_row(self):
        dird_result = {"column_types": ["name",
                                        "name",
                                        "number_office",
                                        "number_mobile",
                                        "favorite",
                                        "personal"],
                       "column_headers": ["Firstname",
                                          "Lastname",
                                          "Number",
                                          "Number",
                                          "Favorite",
                                          "Personal"]}

        headers = self.formatter.format_headers(dird_result)

        assert_that(headers, contains(('Firstname', 'name'),
                                      ('Lastname', 'name'),
                                      ('Number', 'number')))

    def test_format_headers_no_number(self):
        dird_result = {"column_types": ["name",
                                        "name",
                                        "favorite",
                                        "personal"],
                       "column_headers": ["Firstname",
                                          "Lastname",
                                          "Favorite",
                                          "Personal"]}

        headers = self.formatter.format_headers(dird_result)

        assert_that(headers, contains(('Firstname', 'name'),
                                      ('Lastname', 'name')))
