# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import assert_that, equal_to
from mock import Mock
from xivo_cti.call_forms.dispatch_filter import DispatchFilter
from xivo_cti.services.bridge.event import BridgeEvent
from xivo_cti.services.bridge.notifier import BridgeNotifier
from xivo_cti.services.call.receiver import CallReceiver
from xivo_cti.services.current_call.manager import CurrentCallManager


class TestBridgeNotifier(unittest.TestCase):

    def setUp(self):
        self.call_form_dispatch_filter = Mock(DispatchFilter)
        self.call_receiver = Mock(CallReceiver)
        self.current_call_manager = Mock(CurrentCallManager)
        self.bridge = Mock()
        self.channel = Mock()
        self.bridge_notifier = BridgeNotifier(self.call_form_dispatch_filter,
                                              self.call_receiver,
                                              self.current_call_manager)

    def test_on_bridge_enter_linked(self):
        bridge_link_event = BridgeEvent(self.bridge, self.channel)

        self.bridge_notifier._on_bridge_enter(self.bridge, self.channel, True)

        self.call_form_dispatch_filter.handle_bridge_link.assert_called_once_with(bridge_link_event)
        self.call_receiver.handle_bridge_link.assert_called_once_with(bridge_link_event)
        self.current_call_manager.handle_bridge_link.assert_called_once_with(bridge_link_event)

    def test_on_bridge_enter_not_linked(self):
        self.bridge_notifier._on_bridge_enter(self.bridge, self.channel, False)

        assert_that(self.call_form_dispatch_filter.handle_bridge_link.called, equal_to(False))

    def test_on_bridge_leave_unlinked(self):
        bridge_link_event = BridgeEvent(self.bridge, self.channel)

        self.bridge_notifier._on_bridge_leave(self.bridge, self.channel, True)

        self.call_receiver.handle_bridge_unlink.assert_called_once_with(bridge_link_event)

    def test_on_bridge_leave_not_unlinked(self):
        self.bridge_notifier._on_bridge_leave(self.bridge, self.channel, False)

        assert_that(self.call_receiver.handle_bridge_unlink.called, equal_to(False))
