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

from hamcrest import assert_that
from hamcrest import equal_to
from xivo_cti.cti.commands.call_form_result import CallFormResult


class TestCallFormResult(unittest.TestCase):

    def setUp(self):
        self._commandid = 1234556678
        self._variables = {
            'XIVOFORM_lastname': 'Manning',
            'XIVOFORM_firstname': 'Preston',
        }
        self._message = {
            'class': 'call_form_result',
            'commandid': self._commandid,
            'infos': {
                'buttonname': 'saveandclose',
                'variables': self._variables,
            },
        }

    def test_from_dict(self):
        call_form_result = CallFormResult.from_dict(self._message)

        assert_that(call_form_result.variables, equal_to(self._variables))
