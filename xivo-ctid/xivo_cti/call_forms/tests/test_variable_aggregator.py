# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from hamcrest import assert_that
from hamcrest import equal_to
from mock import sentinel
from xivo_cti.call_forms.variable_aggregator import VariableAggregator
from xivo_cti.call_forms.variable_aggregator import CallFormVariable as Var


class TestVariableAggregator(unittest.TestCase):

    def setUp(self):
        self._va = VariableAggregator()

    def test_set(self):
        self._va.set(sentinel.uid, Var(sentinel.type, sentinel.name, sentinel.value))

        assert_that(self._va.get(sentinel.uid), equal_to({sentinel.type: {sentinel.name: sentinel.value}}))

    def test_get_not_tracked(self):
        assert_that(self._va.get(sentinel.uid), equal_to({}))

    def test_clean(self):
        self._va.set(sentinel.uid, Var(sentinel.type, sentinel.name, sentinel.value))

        self._va.clean(sentinel.uid)

        assert_that(self._va._vars, equal_to({}))

    def test_clean_unknown(self):
        self._va.clean(sentinel.uid)

        assert_that(self._va._vars, equal_to({}))
