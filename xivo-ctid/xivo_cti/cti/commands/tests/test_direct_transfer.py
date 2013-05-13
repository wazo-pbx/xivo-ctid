# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from xivo_cti.cti.commands.direct_transfer import DirectTransfer


class TestDirectTransfer(unittest.TestCase):

    def setUp(self):
        self.commandid = 5664346
        self.number = '5431'
        self.direct_transfer_message = {
            'class': 'direct_transfer',
            'commandid': self.commandid,
            'number': self.number,
        }

    def test_from_dict(self):
        direct_transfer = DirectTransfer.from_dict(self.direct_transfer_message)

        self.assertEqual(direct_transfer.commandid, self.commandid)
        self.assertEqual(direct_transfer.number, self.number)
