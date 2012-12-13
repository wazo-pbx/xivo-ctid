# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
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
from mock import Mock

from xivo_cti.tools.delta_computer import DictDelta, DeltaComputer


class TestDeltaComputer(unittest.TestCase):

    def test_compute_delta_empty_empty(self):
        new_dict = {}
        old_dict = {}
        expected_result = DictDelta({}, {}, {})

        result = DeltaComputer.compute_delta(new_dict, old_dict)

        self.assertEqual(result, expected_result)

    def test_compute_delta_add(self):
        new_dict = {'old_key': 'old_value', 'new_key': 'new_value'}
        old_dict = {'old_key': 'old_value'}
        expected_result = DictDelta({'new_key': 'new_value'}, {}, {})

        result = DeltaComputer.compute_delta(new_dict, old_dict)

        self.assertEqual(result, expected_result)

    def test_compute_delta_delete(self):
        new_dict = {'old_key': 'old_value'}
        old_dict = {'old_key': 'old_value', 'removed_key': 'removed_value'}
        expected_result = DictDelta({}, {}, {'removed_key': 'removed_value'})

        result = DeltaComputer.compute_delta(new_dict, old_dict)

        self.assertEqual(result, expected_result)

    def test_compute_delta_change(self):
        new_dict = {'same_key1': 'same_value', 'same_key2': 'new_value'}
        old_dict = {'same_key1': 'same_value', 'same_key2': 'old_value'}
        expected_result = DictDelta({}, {'same_key2': 'new_value'}, {})

        result = DeltaComputer.compute_delta(new_dict, old_dict)

        self.assertEqual(result, expected_result)

    def test_compute_delta_change_and_add(self):
        new_dict = {'same_key1': 'same_value', 'same_key2': 'new_value', 'new_key': 'new_value'}
        old_dict = {'same_key1': 'same_value', 'same_key2': 'old_value'}
        expected_result = DictDelta({'new_key': 'new_value'}, {'same_key2': 'new_value'}, {})

        result = DeltaComputer.compute_delta(new_dict, old_dict)

        self.assertEqual(result, expected_result)

    def test_compute_delta_no_delete_add(self):
        new_dict = {'old_key': 'old_value', 'new_key': 'new_value'}
        old_dict = {'old_key': 'old_value'}
        expected_result = DictDelta({'new_key': 'new_value'}, {}, {})

        result = DeltaComputer.compute_delta_no_delete(new_dict, old_dict)

        self.assertEqual(result, expected_result)

    def test_compute_delta_no_delete_delete(self):
        new_dict = {'old_key': 'old_value'}
        old_dict = {'old_key': 'old_value', 'removed_key': 'removed_value'}
        expected_result = DictDelta({}, {}, {})

        result = DeltaComputer.compute_delta_no_delete(new_dict, old_dict)

        self.assertEqual(result, expected_result)

    def test_compute_delta_no_delete_change(self):
        new_dict = {'same_key1': 'same_value', 'same_key2': 'new_value'}
        old_dict = {'same_key1': 'same_value', 'same_key2': 'old_value'}
        expected_result = DictDelta({}, {'same_key2': 'new_value'}, {})

        result = DeltaComputer.compute_delta_no_delete(new_dict, old_dict)

        self.assertEqual(result, expected_result)

    def test_compute_delta_no_delete_change_and_add(self):
        new_dict = {'same_key1': 'same_value', 'same_key2': 'new_value', 'new_key': 'new_value'}
        old_dict = {'same_key1': 'same_value', 'same_key2': 'old_value'}
        expected_result = DictDelta({'new_key': 'new_value'}, {'same_key2': 'new_value'}, {})

        result = DeltaComputer.compute_delta_no_delete(new_dict, old_dict)

        self.assertEqual(result, expected_result)

    def test_compute_delta_no_delete_change_and_remove(self):
        new_dict = {'same_key1': 'same_value', 'same_key2': 'new_value'}
        old_dict = {'same_key1': 'same_value', 'same_key2': 'old_value', 'removed_key': 'removed_value'}
        expected_result = DictDelta({}, {'same_key2': 'new_value'}, {})

        result = DeltaComputer.compute_delta_no_delete(new_dict, old_dict)

        self.assertEqual(result, expected_result)

    def test_compute_delta_no_delete_add_and_remove(self):
        new_dict = {'new_key': 'new_value'}
        old_dict = {'removed_key': 'removed_value'}
        expected_result = DictDelta({'new_key': 'new_value'}, {}, {})

        result = DeltaComputer.compute_delta_no_delete(new_dict, old_dict)

        self.assertEqual(result, expected_result)

    def test_compute_delta_no_delete_add_change_and_remove(self):
        new_dict = {'new_key': 'new_value', 'same_key': 'new_value'}
        old_dict = {'removed_key': 'removed_value', 'same_key': 'old_value'}
        expected_result = DictDelta({'new_key': 'new_value'}, {'same_key': 'new_value'}, {})

        result = DeltaComputer.compute_delta_no_delete(new_dict, old_dict)

        self.assertEqual(result, expected_result)
