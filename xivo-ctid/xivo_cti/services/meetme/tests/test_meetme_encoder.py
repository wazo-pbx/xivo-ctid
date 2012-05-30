# -*- coding: utf-8 -*-
# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from xivo_cti.services.meetme import encoder


class TestMeetmeEncoder(unittest.TestCase):

    def test_encode_update(self):
        config = {'800': {'number': '800',
                          'name': 'my_test_conf',
                          'pin_required': True,
                          'start_time': 1234.1234,
                          'members': {1: {'join_order': 1,
                                          'join_time': 1234.1234,
                                          'number': '1002',
                                          'name': 'Tester 1',
                                          'channel': 'SIP/jsdhfjd-124',
                                          'muted': True},
                                      2: {'join_order': 2,
                                          'join_time': 1239.1234,
                                          'number': '4181235555',
                                          'name': '4181235555',
                                          'channel': 'DAHDI/i1/4181235555-5',
                                          'muted': False}}}}

        result = encoder.encode_update(config)

        expected = {'class': 'meetme_update',
                    'config': {'800': {'number': '800',
                                       'name': 'my_test_conf',
                                       'pin_required': 'Yes',
                                       'start_time': 1234.1234,
                                       'member_count': 2,
                                       'members': {1: {'join_order': 1,
                                                       'join_time': 1234.1234,
                                                       'number': '1002',
                                                       'name': 'Tester 1',
                                                       'muted': 'Yes'},
                                                   2: {'join_order': 2,
                                                       'join_time': 1239.1234,
                                                       'number': '4181235555',
                                                       'name': '4181235555',
                                                       'muted': 'No'}}}}}

        self.assertEqual(result, expected)

    def test_encode_user(self):
        result = encoder.encode_user('800', 2)

        expected = {'class': 'meetme_user',
                    'meetme': '800',
                    'usernum': 2}

        self.assertEqual(expected, result)

    def test_swap_bool_to_yes_no(self):
        YES, NO = 'Yes', 'No'
        start = {'one': True,
                 'two': 1,
                 'three': False,
                 'four': 0,
                 'five': '',
                 'six': {True: True,
                         False: False},
                 'seven': {'nested_one': True,
                           'nested_two': {'nested_three': True,
                                          'nested_four': False}}}

        expected = {'one': YES,
                    'two': 1,
                    'three': NO,
                    'four': 0,
                    'five': '',
                    'six': {True: YES,
                            False: NO},
                    'seven': {'nested_one': YES,
                              'nested_two': {'nested_three': YES,
                                             'nested_four': NO}}}

        result = encoder._swap_bool_to_yes_no(start)

        self.assertEqual(result, expected)
