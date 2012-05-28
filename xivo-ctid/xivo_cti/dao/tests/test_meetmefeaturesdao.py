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

from xivo_cti.dao import meetmefeaturesdao
from xivo_cti.dao.alchemy import dbconnection
from xivo_cti.dao.alchemy.base import Base
from xivo_cti.dao.alchemy.meetmefeatures import MeetmeFeatures


class TestmeetmesionsDAO(unittest.TestCase):

    def setUp(self):
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        connection = dbconnection.get_connection('asterisk')

        Base.metadata.drop_all(connection.get_engine(), [MeetmeFeatures.__table__])
        Base.metadata.create_all(connection.get_engine(), [MeetmeFeatures.__table__])

        self.session = connection.get_session()

        self.session.commit()

    def tearDown(self):
        dbconnection.unregister_db_connection_pool()

    def _insert_meetme(self, meetmeid, name, confno):
        meetme = MeetmeFeatures()
        meetme.meetmeid = meetmeid
        meetme.name = name
        meetme.confno = confno
        self.session.add(meetme)
        self.session.commit()
        return meetme.id

    def test_get_one_result(self):
        user_id = self._insert_meetme(1, 'red', '9000')

        user = meetmefeaturesdao.get(user_id)

        self.assertEqual(user.id, user_id)

    def test_get_string_id(self):
        user_id = self._insert_meetme(1, 'red', '9000')

        user = meetmefeaturesdao.get(str(user_id))

        self.assertEqual(user.id, user_id)

    def test_get_no_result(self):
        self.assertRaises(LookupError, lambda: meetmefeaturesdao.get(1))

    def test_find_by_name(self):
        self._insert_meetme(1, 'red', '9000')
        self._insert_meetme(2, 'blue', '9001')

        meetme_red = meetmefeaturesdao.find_by_name('red')
        meetme_blue = meetmefeaturesdao.find_by_name('blue')

        self.assertEqual(meetme_red.name, 'red')
        self.assertEqual(meetme_blue.name, 'blue')

    def test_find_by_confno(self):
        self._insert_meetme(1, 'red', '9000')
        self._insert_meetme(2, 'blue', '9001')

        meetme_red = meetmefeaturesdao.find_by_confno('9000')
        meetme_blue = meetmefeaturesdao.find_by_confno('9001')

        self.assertEqual(meetme_red.confno, '9000')
        self.assertEqual(meetme_blue.confno, '9001')
