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

from xivo_cti import innerdata
from xivo_cti import channel_updater


class TestChannelUpdater(unittest.TestCase):

    def setUp(self):
        self.innerdata = Mock(innerdata.Safe)
        self.updater = channel_updater.ChannelUpdater(self.innerdata)

    def test_new_caller_id(self):
        channel_1 = {
            'name': 'SIP/abc-124',
            'context': 'test',
            'unique_id': 12798734.33
        }
        self.innerdata.channels = {
            channel_1['name']: innerdata.Channel(channel_1['name'],
                                                 channel_1['context'],
                                                 channel_1['unique_id'])
        }

        self.updater.new_caller_id(channel_1['name'],
                                   'Alice',
                                   '1234')

        channel = self.innerdata.channels[channel_1['name']]
        self.assertEqual(channel.extra_data['xivo']['calleridname'], 'Alice')
        self.assertEqual(channel.extra_data['xivo']['calleridnum'], '1234')

    def test_new_caller_id_unknown_channel(self):
        channel_1 = {
            'name': 'SIP/abc-124',
            'context': 'test',
            'unique_id': 12798734.33
        }
        self.innerdata.channels = {
        }

        try:
            self.updater.new_caller_id(channel_1['name'],
                                       'Alice',
                                       '1234')
        except:
            self.fail('Should not raise')
