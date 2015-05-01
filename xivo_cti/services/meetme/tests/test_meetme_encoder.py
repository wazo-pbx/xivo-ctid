# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

from xivo_cti.services.meetme import encoder


class TestMeetmeEncoder(unittest.TestCase):

    def test_encode_update(self):
        config = {'800': {'number': '800',
                          'name': 'my_test_conf',
                          'pin_required': True,
                          'start_time': 1234.1234,
                          'context': 'my_secret_context',
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
                                       'pin_required': True,
                                       'start_time': 1234.1234,
                                       'member_count': 2,
                                       'members': {'1': {'join_order': 1,
                                                         'join_time': 1234.1234,
                                                         'number': '1002',
                                                         'name': 'Tester 1',
                                                         'muted': True},
                                                   '2': {'join_order': 2,
                                                         'join_time': 1239.1234,
                                                         'number': '4181235555',
                                                         'name': '4181235555',
                                                         'muted': False}}}}}

        self.assertEqual(result, expected)

    def test_encode_update_for_contexts(self):
        config = {'800': {'number': '800',
                          'name': 'my_test_conf',
                          'pin_required': True,
                          'start_time': 1234.1234,
                          'context': 'my_secret_context',
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
                                          'muted': False}}},
                  '801': {'number': '801',
                          'name': 'conf 801',
                          'pin_required': False,
                          'start_time': 0,
                          'context': 'default',
                          'members': {}}}

        result = encoder.encode_update_for_contexts(config, ['no_conf'])

        self.assertEqual(result, {'class': 'meetme_update',
                                  'config': {}})

        result = encoder.encode_update_for_contexts(config, ['default'])

        self.assertEqual(result, {'class': 'meetme_update',
                                  'config': {'801': {'number': '801',
                                                     'name': 'conf 801',
                                                     'pin_required': False,
                                                     'start_time': 0,
                                                     'member_count': 0,
                                                     'members': {}}}})

    def test_encode_user(self):
        result = encoder.encode_user('800', 2)

        expected = {'class': 'meetme_user',
                    'meetme': '800',
                    'usernum': 2}

        self.assertEqual(expected, result)

    def test_encode_room_number_pairs(self):
        pairs = [('800', 1), ('802', 1)]
        expected = {'class': 'meetme_user',
                    'list': sorted([{'room_number': '800',
                                     'user_number': 1},
                                    {'room_number': '802',
                                     'user_number': 1}])}

        result = encoder.encode_room_number_pairs(pairs)

        self.assertEqual(result, expected)
