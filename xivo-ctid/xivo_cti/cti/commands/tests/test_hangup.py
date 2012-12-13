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

from xivo_cti.cti.commands.hangup import Hangup


class TestHangup(unittest.TestCase):

    def setUp(self):
        self.commandid = 125731893
        self.hangup_message = {
            'class': 'hangup',
            'commandid': self.commandid,
            'ipbxid': 'xivo',
            'userid': '1'
        }

    def test_answer(self):
        self.assertEqual(Hangup.COMMAND_CLASS, 'hangup')

    def test_from_dict(self):
        hangup = Hangup.from_dict(self.hangup_message)

        self.assertEqual(hangup.commandid, self.commandid)
