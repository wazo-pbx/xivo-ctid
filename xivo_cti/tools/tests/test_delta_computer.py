# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
