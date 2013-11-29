# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from hamcrest import assert_that, equal_to, same_instance
from mock import sentinel
from unittest import TestCase

from ..calls import ReceivedCall, SentCall


class TestReceivedCall(TestCase):
    def test_display_other_end(self):
        call = ReceivedCall(sentinel.date,
                            sentinel.duration,
                            sentinel.caller_name)

        result = call.display_other_end()

        assert_that(result, same_instance(sentinel.caller_name))

    def test_equal(self):
        call = ReceivedCall(sentinel.date,
                            sentinel.duration,
                            sentinel.caller_name)
        call_clone = ReceivedCall(sentinel.date,
                                  sentinel.duration,
                                  sentinel.caller_name)

        result = call == call_clone

        assert_that(result, equal_to(True))

    def test_not_equal(self):
        call = ReceivedCall(sentinel.date,
                            sentinel.duration,
                            sentinel.caller_name)
        call_clone = ReceivedCall(sentinel.date,
                                  sentinel.duration,
                                  sentinel.caller_name)

        result = call != call_clone

        assert_that(result, equal_to(False))


class TestSentCall(TestCase):
    def test_display_other_end(self):
        call = SentCall(sentinel.date,
                        sentinel.duration,
                        sentinel.extension)

        result = call.display_other_end()

        assert_that(result, same_instance(sentinel.extension))

    def test_equal(self):
        call = SentCall(sentinel.date,
                        sentinel.duration,
                        sentinel.extension)
        call_clone = SentCall(sentinel.date,
                              sentinel.duration,
                              sentinel.extension)

        assert_that(call, equal_to(call_clone))

    def test_not_equal(self):
        call = SentCall(sentinel.date,
                        sentinel.duration,
                        sentinel.caller_name)
        call_clone = SentCall(sentinel.date,
                              sentinel.duration,
                              sentinel.caller_name)

        result = call != call_clone

        assert_that(result, equal_to(False))
