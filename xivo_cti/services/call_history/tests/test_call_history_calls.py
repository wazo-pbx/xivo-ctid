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

from hamcrest import assert_that, equal_to
from mock import sentinel
from unittest import TestCase

from ..calls import AllCall


class TestAllCall(TestCase):
    def test_equal(self):
        call = AllCall(sentinel.date,
                       sentinel.duration,
                       sentinel.caller_name,
                       sentinel.extension,
                       sentinel.mode)
        call_clone = AllCall(sentinel.date,
                             sentinel.duration,
                             sentinel.caller_name,
                             sentinel.extension,
                             sentinel.mode)

        result = call == call_clone

        assert_that(result, equal_to(True))

    def test_not_equal(self):
        call = AllCall(sentinel.date,
                       sentinel.duration,
                       sentinel.caller_name,
                       sentinel.extension,
                       sentinel.mode)
        call_clone = AllCall(sentinel.date,
                             sentinel.duration,
                             sentinel.caller_name,
                             sentinel.extension,
                             sentinel.mode)

        result = call != call_clone

        assert_that(result, equal_to(False))
