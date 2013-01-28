# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from xivo_cti.cti.commands.subscribe_current_calls import SubscribeCurrentCalls


class TestSubscribeCurrentCalls(unittest.TestCase):

    MSG = {'class': 'subscribe',
           'message': 'current_calls'}

    def test_init_from_dict(self):
        sub_msg = SubscribeCurrentCalls.from_dict(self.MSG)

        self.assertEqual(sub_msg.message, 'current_calls')
