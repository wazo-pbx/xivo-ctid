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

from xivo_cti.cti.commands.unhold_switchboard import UnholdSwitchboard


class TestUnholdSwitchboard(unittest.TestCase):

    def setUp(self):
        self.commandid = 125731893
        self.unhold_switchboard_message = {
            'class': 'unhold_switchboard',
            'unique_id': '123456.66',
            'commandid': self.commandid,
        }

    def test_unhold_switchboard(self):
        self.assertEqual(UnholdSwitchboard.COMMAND_CLASS, 'unhold_switchboard')

    def test_from_dict(self):
        unhold_switchboard = UnholdSwitchboard.from_dict(self.unhold_switchboard_message)

        self.assertEqual(unhold_switchboard.commandid, self.commandid)
        self.assertEqual(unhold_switchboard.unique_id, self.unhold_switchboard_message['unique_id'])