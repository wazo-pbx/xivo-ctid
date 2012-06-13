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

from xivo_cti.dao.tests.test_dao import DAOTestCase
from xivo_cti.dao.alchemy.groupfeatures import GroupFeatures
from xivo_cti.dao.alchemy import dbconnection
from xivo_cti.dao import group_dao


class TestGroupDAO(DAOTestCase):

    required_tables = [GroupFeatures.__table__]

    def setUp(self):
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        connection = dbconnection.get_connection('asterisk')

        self.cleanTables()

        self.session = connection.get_session()

        self.session.commit()
        self.session = connection.get_session()

    def test_get_name(self):
        group = GroupFeatures()
        group.name = 'test_name'
        group.number = '1234'
        group.context = 'my_ctx'

        self.session.add(group)
        self.session.commit()

        result = group_dao.get_name(group.id)

        self.assertEqual(result, group.name)
