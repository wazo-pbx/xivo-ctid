# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, equal_to
from mock import sentinel
from unittest import TestCase

from ..calls import Call


class TestCall(TestCase):

    def test_equal(self):
        call = Call(sentinel.date,
                    sentinel.duration,
                    sentinel.caller_name,
                    sentinel.extension,
                    sentinel.mode)
        call_clone = Call(sentinel.date,
                          sentinel.duration,
                          sentinel.caller_name,
                          sentinel.extension,
                          sentinel.mode)

        assert_that(call_clone, equal_to(call))

    def test_not_equal(self):
        call = Call(sentinel.date,
                    sentinel.duration,
                    sentinel.caller_name,
                    sentinel.extension,
                    sentinel.mode)
        call_clone = Call(sentinel.date,
                          sentinel.duration,
                          sentinel.caller_name,
                          sentinel.extension,
                          sentinel.mode)

        result = call != call_clone

        assert_that(result, equal_to(False))
