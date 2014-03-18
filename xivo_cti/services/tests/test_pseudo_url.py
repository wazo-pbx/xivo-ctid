# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from xivo_cti.model.destination import Destination
from xivo_cti.services.pseudo_url import PseudoURL


class TestPseudoURL(unittest.TestCase):

    def setUp(self):
        self._ipbxid = 'xivo'

    def test_parse_url_exten(self):
        exten = '1234'
        exten_url = 'exten:{0}/{1}'.format(self._ipbxid, exten)

        expected = Destination('exten', self._ipbxid, exten)

        assert_that(PseudoURL.parse(exten_url), equal_to(expected), 'Parsed exten URL')

    def test_parse_url_invalid(self):
        self.assertRaises(ValueError, PseudoURL.parse, '1234')
