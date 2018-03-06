# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import all_of
from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import has_property
from hamcrest import is_not
from mock import Mock
from mock import sentinel
from xivo.asterisk.extension import Extension
from xivo_cti.services.call.call import Call
from xivo_cti.services.call.call import _Channel


class TestChannel(unittest.TestCase):

    def test_channel_simple_attributes(self):
        channel = _Channel(sentinel.exten, sentinel.channel_name)

        assert_that(channel, all_of(
            has_property('extension', sentinel.exten),
            has_property('_channel', sentinel.channel_name),
        ))

    def test_equality(self):
        assert_that(_Channel(sentinel.exten, sentinel.channel), all_of(
            equal_to(_Channel(sentinel.exten, sentinel.channel)),
            is_not(equal_to(_Channel(sentinel.other_exten, sentinel.channel))),
            is_not(equal_to(_Channel(sentinel.exten, sentinel.other_channel))),
            is_not(equal_to(_Channel(sentinel.other_exten, sentinel.other_channel))),
        ))

    def test_repr(self):
        e = Extension('1001', 'default', True)
        assert_that(repr(_Channel(e, 'mychannel')), equal_to('_Channel(1001@default, mychannel)'))


class TestCall(unittest.TestCase):

    def test_call_simple_attributes(self):
        call = Call(sentinel.source, sentinel.destination)

        assert_that(call, all_of(
            has_property('source', sentinel.source),
            has_property('destination', sentinel.destination),
        ))

    def test_call_is_internal_both_internal(self):
        self._internal_helper(True, True, True)

    def test_call_is_internal_external_source(self):
        self._internal_helper(False, True, False)

    def test_call_is_internal_external_destination(self):
        self._internal_helper(True, False, False)

    def test_call_is_internal_both_external(self):
        self._internal_helper(False, False, False)

    def _internal_helper(self, source_internal, destination_internal, expected):
        source = _Channel(Mock(Call, is_internal=source_internal), sentinel.channel_name)
        destination = _Channel(Mock(Call, is_internal=destination_internal), sentinel.channel_name)

        call = Call(source, destination)

        assert_that(call.is_internal, equal_to(expected))

    def test_equality(self):
        assert_that(Call(sentinel.source, sentinel.destination), all_of(
            equal_to(Call(sentinel.source, sentinel.destination)),
            is_not(equal_to(Call(sentinel.other_source, sentinel.destination))),
            is_not(equal_to(Call(sentinel.source, sentinel.other_destination))),
            is_not(equal_to(Call(sentinel.other_source, sentinel.other_destination))),
        ))

    def test_inequality(self):
        call = Call(sentinel.source, sentinel.destination)
        other_call = Call(sentinel.other_source, sentinel.destination)
        self.assertTrue(call != other_call)
