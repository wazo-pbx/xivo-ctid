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

from mock import Mock
from mock import patch
from xivo_cti.dao.innerdata_dao import InnerdataDAO
from xivo_cti.innerdata import Safe


class TestInnerdataDAO(unittest.TestCase):

    def setUp(self):
        self.innerdata = Mock(Safe)
        self.innerdata_dao = InnerdataDAO(self.innerdata)

    @patch('xivo_cti.dao.innerdata_dao.config', {'profiles': {'client': {'userstatus': 2}},
                                                 'userstatus': {
                                                     2: {'available': {},
                                                         'disconnected': {}}}})
    def test_get_presences(self):
        profile = 'client'
        expected_result = ['available', 'disconnected']

        result = self.innerdata_dao.get_presences(profile)

        self.assertEquals(result, expected_result)
