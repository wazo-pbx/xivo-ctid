# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
from xivo_cti.cti.commands.user_service.disable_noanswer_forward import DisableNoAnswerForward


class TestDisableNoAnswerForward(unittest.TestCase):

    def test_from_dict(self):
        commandid = 12327
        msg = {"class": "featuresput",
               "commandid": commandid,
               "function": "fwd",
               "value": {'destrna': '27654', 'enablerna': False}}

        disable_noanswer_forward = DisableNoAnswerForward.from_dict(msg)

        self.assertTrue(isinstance(disable_noanswer_forward, DisableNoAnswerForward))

        self.assertEquals(disable_noanswer_forward.destination, '27654')
        self.assertEquals(disable_noanswer_forward.enable, False)
