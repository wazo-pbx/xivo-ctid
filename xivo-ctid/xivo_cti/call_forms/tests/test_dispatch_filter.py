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
from hamcrest import only_contains
from mock import Mock
from mock import sentinel
from xivo_cti.call_forms.dispatch_filter import DispatchFilter
from xivo_cti.innerdata import Safe


class TestDispatchFilter(unittest.TestCase):

    def setUp(self):
        self._innerdata = Mock(Safe)
        self._df = DispatchFilter(self._innerdata)
        self._dispatch = self._df._dispatch = Mock()

    def test_dispatch(self):
        dispatch_filter = DispatchFilter(self._innerdata)

        dispatch_filter._dispatch(sentinel.ev, sentinel.uid)

        self._innerdata.sheetsend.assert_called_once_with(sentinel.ev, sentinel.uid)

    def test_handle_dial_to_user(self):
        self._df.handle_user(sentinel.uid, sentinel.chan)
        self._df.handle_dial(sentinel.uid, sentinel.chan)

        self._dispatch.assert_called_once_with('dial', sentinel.uid)

    def test_handle_dial_to_queue(self):
        self._df.handle_queue(sentinel.uid, sentinel.chan_queue)
        self._dispatch.reset_mock()
        self._df.handle_dial(sentinel.uid, sentinel.chan_dial)

        assert_that(self._dispatch.call_count, equal_to(0))

    def test_handle_did(self):
        self._df.handle_did(sentinel.uid, sentinel.chan)

        self._dispatch.assert_called_once_with('incomingdid', sentinel.uid)

    def test_handle_group(self):
        self._df.handle_group(sentinel.uid, sentinel.chan)

        self._dispatch.assert_called_once_with('dial', sentinel.uid)

    def test_handle_queue(self):
        self._df.handle_queue(sentinel.uid, sentinel.chan)

        self._dispatch.assert_called_once_with('dial', sentinel.uid)

    def test_handle_user(self):
        self._df.handle_user(sentinel.uid, sentinel.chan)

        assert_that(self._df._dispatch.call_count, equal_to(0))

    def test_handle_bridge_call_to_user(self):
        self._df.handle_user(sentinel.uid, sentinel.chan)
        self._df.handle_bridge(sentinel.uid, sentinel.chan)

        self._dispatch.assert_called_once_with('link', sentinel.uid)

    def test_handle_bridge_call_to_user_hold_resume(self):
        self._df.handle_user(sentinel.uid, sentinel.chan)
        self._df.handle_bridge(sentinel.uid, sentinel.chan)
        self._df.handle_bridge(sentinel.uid, sentinel.chan)
        self._df.handle_bridge(sentinel.uid, sentinel.chan)

        self._dispatch.assert_called_once_with('link', sentinel.uid)

    def test_handle_bridge_call_to_queue(self):
        self._df.handle_queue(sentinel.uid, sentinel.chan)
        self._df.handle_bridge(sentinel.uid, sentinel.chan)

        self._dispatch.assert_called_once_with('dial', sentinel.uid)

    def test_handle_bridge_call_to_group(self):
        self._df.handle_group(sentinel.uid, sentinel.chan)
        self._df.handle_bridge(sentinel.uid, sentinel.chan)

        self._dispatch.assert_called_once_with('dial', sentinel.uid)

    def test_handle_agent_connect(self):
        self._df.handle_agent_connect(sentinel.uid, sentinel.chan)

        self._dispatch.assert_called_once_with('link', sentinel.uid)

    def test_handle_agent_complete(self):
        self._df.handle_agent_complete(sentinel.uid, sentinel.chan)

        self._dispatch.assert_called_once_with('unlink', sentinel.uid)

    def test_handle_hangup(self):
        self._df._linked_calls = [sentinel.uid, sentinel.uid2]
        self._df._calls_to_user = {
            sentinel.uid: True,
            sentinel.uid2: True,
        }
        chan = 'SCCP/12432@notdefault-2334'
        self._df.handle_hangup(sentinel.uid, chan)

        self._dispatch.assert_called_once_with('hangup', sentinel.uid)

        assert_that(self._df._linked_calls, only_contains(sentinel.uid2))
        assert_that(self._df._calls_to_user, equal_to({sentinel.uid2: True}))

    def test_hangle_hangup_agent_callback(self):
        self._df.handle_hangup(sentinel.uid, 'Local/id-1@agentcallback-54354;1')

        assert_that(self._dispatch.call_count, equal_to(0))
