# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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

from xivo_cti.tools.extension import normalize_exten
from xivo_cti.tools.extension import InvalidExtension


class TestInvalidExtension(unittest.TestCase):
    def test_exten_attribute(self):
        self.assertEqual(InvalidExtension('1234').exten, '1234')


class TestExtension(unittest.TestCase):

    def test_normalize_exten(self):
        extens = ['00.11.22.33.44',
                  '00 11 22 33 44',
                  '00-_11@%^& 22":<>/33?:";44']
        for exten in extens:
            self.assertEqual(normalize_exten(exten), '0011223344')

    def test_normalize_exten_with_plus(self):
        extens = ['+00.11.22.33.44',
                  '+00 11 22 33 44',
                  '+00-_11@%^& 22":<>/33?:";44']
        for exten in extens:
            self.assertEqual(normalize_exten(exten), '+0011223344')

    def test_normalize_exten_any_valid_char(self):
        exten = '-@%^& ":<>/?:";'
        self.assertRaises(InvalidExtension, normalize_exten, exten)

    def test_normalize_exten_caller_id(self):
        exten = '"User 1" <1001>"'
        self.assertEqual(normalize_exten(exten), '1001')
