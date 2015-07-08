# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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

from mock import Mock, call, sentinel
from hamcrest import assert_that
from hamcrest import equal_to

from xivo_cti import innerdata
from xivo_cti import channel_updater
from xivo_cti.call_forms.variable_aggregator import CallFormVariable as Var
from xivo_cti.call_forms.variable_aggregator import VariableAggregator
from xivo_cti.channel import Channel
from xivo_cti.channel_updater import assert_has_channel


class TestAssertHasChannelDecorator(unittest.TestCase):

    def setUp(self):
        self.original = Mock()
        self.decorated = assert_has_channel(self.original)
        self.channel_name = 'SIP/abc-123'
        self.updater = Mock()

    def test_assert_has_channel(self):
        self.updater.innerdata.channels = {self.channel_name: 1}

        self.decorated(self.updater, self.channel_name, sentinel.arg)

        self.original.assert_called_once_with(self.updater, self.channel_name, sentinel.arg)

    def test_assert_has_channel_not_found(self):
        self.updater.innerdata.channels = {}

        self.decorated(self.updater, self.channel_name, sentinel.arg)

        self.assertFalse(self.original.called)


class TestChannelUpdater(unittest.TestCase):

    def setUp(self):
        self.innerdata = Mock(innerdata.Safe)
        self.innerdata.channels = {}
        self._va = VariableAggregator()
        self.updater = channel_updater.ChannelUpdater(self.innerdata, self._va)

    def test_new_caller_id(self):
        uid = 127984.33
        self._va.set(uid, Var('xivo', 'calleridname', 'Paul'))
        self._va.set(uid, Var('xivo', 'calleridnum', '666'))

        self.updater.new_caller_id(uid, sentinel.name, sentinel.num)

        assert_that(self._va.get(uid)['xivo']['calleridname'], equal_to(sentinel.name))
        assert_that(self._va.get(uid)['xivo']['calleridnum'], equal_to(sentinel.num))

    def test_new_caller_id_no_cid_name(self):
        uid = 127984.33
        self._va.set(uid, Var('xivo', 'calleridname', sentinel.name))
        self._va.set(uid, Var('xivo', 'calleridnum', '666'))

        self.updater.new_caller_id(uid, '', sentinel.num)

        assert_that(self._va.get(uid)['xivo']['calleridname'], equal_to(sentinel.name))
        assert_that(self._va.get(uid)['xivo']['calleridnum'], equal_to(sentinel.num))

    def test_reverse_lookup_result(self):
        uid = 2378634.55
        event = {
            'db-reverse': 'rev',
            'db-fullname': 'Pierre Laroche',
            'db-mail': 'pierre@home.com',
            'dp-not-db': 'lol',
        }

        self.updater.reverse_lookup_result(uid, event)

        assert_that(self._va.get(uid)['db'], equal_to({
            'reverse': 'rev',
            'fullname': 'Pierre Laroche',
            'mail': 'pierre@home.com',
        }))

    def test_new_caller_id_unknown_channel(self):
        self.updater.new_caller_id('SIP/1234', 'Alice', '1234')

    def test_hold_channel(self):
        name = 'SIP/1234'
        channel = Channel(name, 'default', '123456.66')
        self.innerdata.channels[name] = channel

        self.updater.set_hold(name)

        channel = self.innerdata.channels[name]
        assert_that(channel.properties['holded'], equal_to(True), 'holded status')
        self._assert_channel_updated(name)

    def test_unhold_channel(self):
        name = 'SIP/1234'
        channel = Channel(name, 'default', '123456.66')
        self.innerdata.channels[name] = channel

        self.updater.set_unhold(name)

        channel = self.innerdata.channels[name]
        assert_that(channel.properties['holded'], equal_to(False), 'unholded status')
        self._assert_channel_updated(name)

    def _assert_channel_updated(self, channel):
        calls = list(self.innerdata.handle_cti_stack.call_args_list)
        expected = [call('setforce', ('channels', 'updatestatus', channel)),
                    call('empty_stack')]

        assert_that(calls, equal_to(expected), 'handle_cti_stack calls')
