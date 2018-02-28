# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, sentinel
from hamcrest import assert_that
from hamcrest import equal_to

from xivo_cti import innerdata
from xivo_cti import channel_updater
from xivo_cti.call_forms.variable_aggregator import CallFormVariable as Var
from xivo_cti.call_forms.variable_aggregator import VariableAggregator


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
