# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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
        self._var = Var(sentinel.type, sentinel.name, sentinel.value)

    def test_set(self):
        self._va.set(sentinel.uid, self._var)

        assert_that(self._va.get(sentinel.uid), equal_to({sentinel.type: {sentinel.name: sentinel.value}}))

    def test_get_not_tracked(self):
        assert_that(self._va.get(sentinel.uid), equal_to({}))

    def test_on_hangup(self):
        self._va.set(sentinel.uid, self._var)

        self._va.on_hangup(sentinel.uid)

        assert_that(self._va._vars, equal_to({}))

    def test_on_hangup_unknown(self):
        self._va.on_hangup(sentinel.uid)

        assert_that(self._va._vars, equal_to({}))

    def test_var_is_available_when_hangup_called_after_agent_connect(self):
        self._va.set(sentinel.uid, self._var)

        self._va.on_agent_connect(sentinel.uid)
        self._va.on_hangup(sentinel.uid)

        assert_that(self._va.get(sentinel.uid), equal_to({sentinel.type: {sentinel.name: sentinel.value}}))

    def test_var_is_removed_on_agent_scenario(self):
        self._va.set(sentinel.uid, self._var)

        self._va.on_agent_connect(sentinel.uid)
        self._va.on_hangup(sentinel.uid)
        self._va.on_agent_complete(sentinel.uid)

        assert_that(self._va.get(sentinel.uid), equal_to({}))
