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

from xivo_cti.cti.commands.attended_transfer import AttendedTransfer


class TestAttendedTransfer(unittest.TestCase):

    def setUp(self):
        self.commandid = 5664346
        self.number = '1234'
        self.attended_transfer_message = {
            'class': 'attended_transfer',
            'commandid': self.commandid,
            'number': self.number,
        }

    def test_attended_transfer(self):
        self.assertEqual(AttendedTransfer.COMMAND_CLASS, 'attended_transfer')

    def test_from_dict(self):
        attended_transfer = AttendedTransfer.from_dict(self.attended_transfer_message)

        self.assertEqual(attended_transfer.commandid, self.commandid)
        self.assertEqual(attended_transfer.number, self.number)
