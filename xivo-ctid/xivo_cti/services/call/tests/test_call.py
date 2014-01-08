# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from mock import Mock
from xivo_cti.services.call.call import Call


class TestCall(unittest.TestCase):

    def setUp(self):
        pass

    def test_call_simple_attributes(self):
        source = Mock()
        destination = Mock()

        call = Call(source, destination)

        self.assertEquals(source, call.source)
        self.assertEquals(destination, call.destination)

    def test_call_is_internal_both_internal(self):
        source = Mock()
        source.is_internal = True
        destination = Mock()
        destination.is_internal = True
        expected_result = True

        call = Call(source, destination)
        result = call.is_internal

        self.assertEquals(expected_result, result)

    def test_call_is_internal_external_source(self):
        source = Mock()
        source.is_internal = False
        destination = Mock()
        destination.is_internal = True
        expected_result = False

        call = Call(source, destination)
        result = call.is_internal

        self.assertEquals(expected_result, result)

    def test_call_is_internal_external_destination(self):
        source = Mock()
        source.is_internal = True
        destination = Mock()
        destination.is_internal = False
        expected_result = False

        call = Call(source, destination)
        result = call.is_internal

        self.assertEquals(expected_result, result)

    def test_call_is_internal_both_external(self):
        source = Mock()
        source.is_internal = False
        destination = Mock()
        destination.is_internal = False
        expected_result = False

        call = Call(source, destination)
        result = call.is_internal

        self.assertEquals(expected_result, result)

    def test_equality_true(self):
        source = Mock()
        destination = Mock()
        call_1 = Call(source, destination)
        call_2 = Call(source, destination)

        self.assertTrue(call_1 == call_2)
        self.assertFalse(call_1 != call_2)

    def test_equality_false_different_sources(self):
        destination = Mock()
        call_1 = Call(source=Mock(), destination=destination)
        call_2 = Call(source=Mock(), destination=destination)

        self.assertTrue(call_1 != call_2)
        self.assertFalse(call_1 == call_2)

    def test_equality_false_different_destinations(self):
        source = Mock()
        call_1 = Call(source=source, destination=Mock())
        call_2 = Call(source=source, destination=Mock())

        self.assertTrue(call_1 != call_2)
        self.assertFalse(call_1 == call_2)
