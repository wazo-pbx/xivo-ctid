# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from mock import Mock
from xivo_cti.dao.channel_dao import ChannelDAO
from xivo_cti import innerdata


class TestChannelDAO(unittest.TestCase):

    def setUp(self):
        self.channel_1 = {'id': 'SIP/abcdef-2135543',
                          'context': 'testctx',
                          'cid_name': 'Alice',
                          'cid_number': '1234'}
        channel_1 = innerdata.Channel(self.channel_1['id'],
                                      self.channel_1['context'])
        channel_1.set_extra_data('xivo', 'calleridname', self.channel_1['cid_name'])
        channel_1.set_extra_data('xivo', 'calleridnum', self.channel_1['cid_number'])

        self.channel_2 = {'id': 'SCCP/123-2135543',
                          'context': 'testctx',
                          'cid_number': '1234'}
        channel_2 = innerdata.Channel(self.channel_2['id'],
                                      self.channel_2['context'])
        channel_2.set_extra_data('xivo', 'calleridnum', self.channel_2['cid_number'])

        self.innerdata = Mock(innerdata.Safe)
        self.innerdata.channels = {
            self.channel_1['id']: channel_1,
            self.channel_2['id']: channel_2,
        }

    def test_get_caller_id_name_number(self):
        channel_dao = ChannelDAO(self.innerdata)

        caller_id = channel_dao.get_caller_id_name_number(self.channel_1['id'])

        self.assertEqual(caller_id[0], self.channel_1['cid_name'])
        self.assertEqual(caller_id[1], self.channel_1['cid_number'])

    def test_get_caller_id_name_number_number_only(self):
        channel_dao = ChannelDAO(self.innerdata)

        caller_id = channel_dao.get_caller_id_name_number(self.channel_2['id'])

        self.assertEqual(caller_id[0], '')
        self.assertEqual(caller_id[1], self.channel_2['cid_number'])

    def test_get_caller_id_name_number_unknown_channel(self):
        channel_dao = ChannelDAO(self.innerdata)

        self.assertRaises(LookupError, channel_dao.get_caller_id_name_number, 'SIP/unknown-1245')
