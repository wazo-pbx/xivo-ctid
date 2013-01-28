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
from xivo_cti.cti.commands.set_user_service import SetUserService


class TestSetUserService(unittest.TestCase):

    def test_init_from_dict(self):
        commandid = 519852486
        msg = {"class": "featuresput",
               "commandid": commandid,
               "function": "enablednd",
               "value": True}

        set_user_service = SetUserService.from_dict(msg)

        self.assertEqual(set_user_service.command_class, SetUserService.COMMAND_CLASS)
        self.assertEqual(set_user_service.function, 'enablednd')
        self.assertEqual(set_user_service.value, True)
