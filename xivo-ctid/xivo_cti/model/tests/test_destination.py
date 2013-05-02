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
from xivo_cti.model.destination import Destination


class TestDestination(unittest.TestCase):

    def test_to_exten_no_error(self):
        d = Destination(1, 2, 3)
        d.to_exten()

    def test_equality(self):
        d1 = Destination('one', 'two', 'three')
        self.assertTrue(d1 == Destination('one', 'two', 'three'))
        self.assertFalse(d1 == Destination('one', 'two', None))
        self.assertFalse(d1 == Destination('one', None, 'three'))
        self.assertFalse(d1 == Destination(None, 'two', 'three'))
