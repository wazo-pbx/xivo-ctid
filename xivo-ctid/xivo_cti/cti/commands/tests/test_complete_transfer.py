# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2013  Avencall
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

from xivo_cti.cti.commands.complete_transfer import CompleteTransfer


class TestCompleteTransfer(unittest.TestCase):

    def setUp(self):
        self.commandid = 678324
        self.complete_transfer_message = {
            'class': 'complete_transfer',
            'commandid': self.commandid,
        }

    def test_complete_transfer(self):
        self.assertEqual(CompleteTransfer.COMMAND_CLASS, 'complete_transfer')

    def test_from_dict(self):
        complete_transfer = CompleteTransfer.from_dict(self.complete_transfer_message)

        self.assertEqual(complete_transfer.commandid, self.commandid)
