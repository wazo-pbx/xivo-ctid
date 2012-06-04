# -*- coding: utf-8 -*-
# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from mock import Mock
from xivo_cti.ctiserver import CTIServer
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.interfaces.interface_cti import NotLoggedException


class TestCTI(unittest.TestCase):

    def setUp(self):
        self._ctiserver = Mock(CTIServer)

    def test_user_id_not_connected(self):
        cti_connection = CTI(self._ctiserver)

        self.assertRaises(NotLoggedException, cti_connection.user_id)

    def test_user_id(self):
        user_id = 5
        cti_connection = CTI(self._ctiserver)
        cti_connection.connection_details['userid'] = user_id

        result = cti_connection.user_id()

        self.assertEqual(result, user_id)
