# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import assert_that, equal_to, is_not
from mock import Mock
from xivo_cti.channel import ChannelRole
from xivo_cti.services.bridge.bridge import Bridge


class TestBridge(unittest.TestCase):

    def setUp(self):
        self.bridge = Bridge('e136cd36-5187-430c-af2a-d1f08870847b', 'basic')
        self.channel_1 = Mock()
        self.channel_2 = Mock()

    def test_add_channel(self):
        self.bridge._add_channel(self.channel_1)

        assert_that(self.bridge.channels, equal_to([self.channel_1]))

    def test_remove_channel(self):
        self.bridge._add_channel(self.channel_1)
        self.bridge._remove_channel(self.channel_1)

        assert_that(self.bridge.channels, equal_to([]))

    def test_remove_channel_non_existent(self):
        self.bridge._remove_channel(self.channel_1)

        assert_that(self.bridge.channels, equal_to([]))

    def test_linked_return_true_with_two_basic_channels(self):
        self.bridge.channels = [self.channel_1, self.channel_2]

        assert_that(self.bridge.linked())

    def test_linked_return_false_when_one_basic_channels(self):
        self.bridge.channels = [self.channel_1]

        assert_that(self.bridge.linked(), equal_to(False))

    def test_caller_and_callee_channel_are_always_different(self):
        roles = [ChannelRole.unknown, ChannelRole.caller, ChannelRole.callee]
        self.bridge.channels = [self.channel_1, self.channel_2]
        for role1 in roles:
            for role2 in roles:
                self.channel_1.role = role1
                self.channel_2.role = role2
                caller = self.bridge.get_caller_channel()
                callee = self.bridge.get_callee_channel()
                assert_that(caller, is_not(equal_to(callee)),
                            'caller and callee equals with roles (%s, %s)' % (role1, role2))

    def test_caller_channel_is_channel_1_when_role_unknown(self):
        self.bridge.channels = [self.channel_1, self.channel_2]
        self.channel_1.role = ChannelRole.unknown
        self.channel_2.role = ChannelRole.unknown

        caller = self.bridge.get_caller_channel()

        assert_that(caller, equal_to(self.channel_1))
