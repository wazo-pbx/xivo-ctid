#!/usr/bin/python
# vim: set fileencoding=utf-8 :

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
from xivo_cti.dao.alchemy import dbconnection
from xivo_cti.dao.alchemy.linefeatures import LineFeatures
from xivo_cti.dao.alchemy.base import Base
from xivo_cti.dao.linefeaturesdao import LineFeaturesDAO
from xivo_cti.dao.alchemy.userfeatures import UserFeatures


class TestLineFeaturesDAO(unittest.TestCase):

    user_id = 5
    line_number = '1666'

    def setUp(self):
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        connection = dbconnection.get_connection('asterisk')

        Base.metadata.drop_all(connection.get_engine(), [LineFeatures.__table__])
        Base.metadata.create_all(connection.get_engine(), [LineFeatures.__table__])

        self.session = connection.get_session()

        self.session.commit()
        self.session = connection.get_session()

        self.dao = LineFeaturesDAO(self.session)

    def tearDown(self):
        dbconnection.unregister_db_connection_pool()

    def test_find_by_user(self):
        user = UserFeatures()
        user.id = self.user_id
        user.firstname = 'test_line'

        line = self._insert_line()

        lines = self.dao.find_by_user(self.user_id)

        self.assertEqual(lines[0], line.id)

    def test_number(self):
        line = self._insert_line()

        number = self.dao.number(line.id)

        self.assertEqual(number, line.number)

    def test_is_phone_exten(self):
        self.assertFalse(self.dao.is_phone_exten('12345'))
        self.assertFalse(self.dao.is_phone_exten(None))

        self._insert_line()

        self.assertTrue(self.dao.is_phone_exten(self.line_number))

    def _insert_line(self):
        line = LineFeatures()
        line.protocolid = 0
        line.name = 'tre321'
        line.context = 'test_context'
        line.provisioningid = 0
        line.number = self.line_number
        line.iduserfeatures = self.user_id

        self.session.add(line)
        self.session.commit()

        return line
