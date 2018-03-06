# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import assert_that
from hamcrest import contains_inanyorder
from mock import Mock
from xivo_cti.call_forms.variable_aggregator import CallFormVariable as Var
from xivo_cti.call_forms.variable_aggregator import VariableAggregator
from xivo_cti.dao.channel_dao import ChannelDAO
from xivo_cti import innerdata
from xivo_cti.channel import Channel


class TestChannelDAO(unittest.TestCase):

    def setUp(self):
        self.channel_1 = {'id': 'SIP/abcdef-2135543',
                          'context': 'testctx',
                          'cid_name': 'Alice',
                          'cid_number': '1234',
                          'unique_id': 786234234.33}
        channel_1 = Channel(self.channel_1['id'],
                            self.channel_1['context'],
                            self.channel_1['unique_id'])
        self.channel_2 = {'id': 'SCCP/123-2135543',
                          'context': 'testctx',
                          'cid_number': '1234',
                          'unique_id': 123456.43}
        channel_2 = Channel(self.channel_2['id'],
                            self.channel_2['context'],
                            self.channel_2['unique_id'])
        self.channel_3 = {'id': 'SCCP/123-9643244',
                          'context': 'testctx',
                          'cid_number': '6543',
                          'unique_id': 987654.32}
        channel_3 = Channel(self.channel_3['id'],
                            self.channel_3['context'],
                            self.channel_3['unique_id'])

        self.innerdata = Mock(innerdata.Safe)
        self.innerdata.channels = {
            self.channel_1['id']: channel_1,
            self.channel_2['id']: channel_2,
            self.channel_3['id']: channel_3,
        }
        self.call_form_variable_aggregator = VariableAggregator()
        self.call_form_variable_aggregator.set(
            self.channel_1['unique_id'],
            Var('xivo', 'calleridname', self.channel_1['cid_name']),
        )
        self.call_form_variable_aggregator.set(
            self.channel_1['unique_id'],
            Var('xivo', 'calleridnum', self.channel_1['cid_number']),
        )
        self.call_form_variable_aggregator.set(
            self.channel_2['unique_id'],
            Var('xivo', 'calleridnum', self.channel_2['cid_number']),
        )
        self._channel_dao = ChannelDAO(self.innerdata, self.call_form_variable_aggregator)

    def test_get_caller_id_name_number(self):
        caller_id = self._channel_dao.get_caller_id_name_number(self.channel_1['id'])

        self.assertEqual(caller_id[0], self.channel_1['cid_name'])
        self.assertEqual(caller_id[1], self.channel_1['cid_number'])

    def test_get_caller_id_name_number_number_only(self):
        caller_id = self._channel_dao.get_caller_id_name_number(self.channel_2['id'])

        self.assertEqual(caller_id[0], '')
        self.assertEqual(caller_id[1], self.channel_2['cid_number'])

    def test_get_caller_id_name_number_unknown_channel(self):
        self.assertRaises(LookupError, self._channel_dao.get_caller_id_name_number, 'SIP/unknown-1245')

    def test_get_channel_from_unique_id(self):
        channel = self._channel_dao.get_channel_from_unique_id(self.channel_1['unique_id'])

        self.assertEqual(channel, self.channel_1['id'])

    def test_get_channel_from_unique_id_unknown(self):
        self.assertRaises(LookupError, self._channel_dao.get_channel_from_unique_id, 'Unknown')

    def test_channels_from_identity_when_no_channels(self):
        result = self._channel_dao.channels_from_identity('sip/unknown-identity')

        self.assertEqual(result, [])

    def test_channels_from_identity_when_one_channel(self):
        result = self._channel_dao.channels_from_identity('sip/abcdef')

        self.assertEqual(result, [self.channel_1['id']])

    def test_channels_from_identity_when_two_channels(self):
        result = self._channel_dao.channels_from_identity('sccp/123')

        assert_that(result, contains_inanyorder(self.channel_2['id'], self.channel_3['id']))
