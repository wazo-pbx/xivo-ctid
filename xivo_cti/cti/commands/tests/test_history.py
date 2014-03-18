# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

from xivo_cti.cti.commands.history import History, HistoryMode


class TestHistory(unittest.TestCase):

    def test_from_dict_incoming(self):
        message = self._build_message(mode='0', size='10')

        history = History.from_dict(message)

        self.assertEqual(history.mode, HistoryMode.outgoing)
        self.assertEqual(history.size, 10)

    def test_from_dict_missing(self):
        message = self._build_message(mode='1', size='20')

        history = History.from_dict(message)

        self.assertEqual(history.mode, HistoryMode.answered)
        self.assertEqual(history.size, 20)

    def test_from_dict_outgoing(self):
        message = self._build_message(mode='2', size='30')

        history = History.from_dict(message)

        self.assertEqual(history.mode, HistoryMode.missed)
        self.assertEqual(history.size, 30)

    def _build_message(self, mode, size):
        return {
            'class': 'ipbxcommand',
            'command': 'history',
            'mode': mode,
            'size': size,
        }
