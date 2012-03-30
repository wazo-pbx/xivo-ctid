# vim: set fileencoding=utf-8 :
# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from xivo_cti.tools.idconverter import IdConverter


class TestIdConverter(unittest.TestCase):
    def test_xid_to_id_input_empty(self):
        identifier = ''
        expected_result = ''

        result = IdConverter.xid_to_id(identifier)

        self.assertEqual(result, expected_result)

    def test_xid_to_id_input_int(self):
        identifier = 12
        expected_result = '12'

        result = IdConverter.xid_to_id(identifier)

        self.assertEqual(result, expected_result)

    def test_xid_to_id_input_id(self):
        identifier = '12'
        expected_result = '12'

        result = IdConverter.xid_to_id(identifier)

        self.assertEqual(result, expected_result)

    def test_xid_to_id_input_xid(self):
        identifier = 'ipbxid/12'
        expected_result = '12'

        result = IdConverter.xid_to_id(identifier)

        self.assertEqual(result, expected_result)
