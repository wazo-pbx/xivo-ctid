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

from xivo_cti.dao.tests import test_dao

from xivo_cti.dao import meetme_features_dao
from xivo_cti.dao.alchemy import dbconnection
from xivo_cti.dao.alchemy.meetmefeatures import MeetmeFeatures
from xivo_cti.dao.alchemy.staticmeetme import StaticMeetme


class TestMeetmeFeaturesDAO(test_dao.DAOTestCase):

    required_tables = [MeetmeFeatures.__table__, StaticMeetme.__table__]

    def setUp(self):
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        connection = dbconnection.get_connection('asterisk')

        self.cleanTables()

        self.session = connection.get_session()

        self.session.commit()

    def tearDown(self):
        dbconnection.unregister_db_connection_pool()

    def _insert_meetme(self, meetmeid, name, confno, pin=None):
        var_val = confno if pin == None else ','.join([confno, pin])
        static_meetme = StaticMeetme()
        static_meetme.category = 'rooms'
        static_meetme.var_name = 'conf'
        static_meetme.var_val = var_val
        static_meetme.filename = 'meetme.conf'
        self.session.add(static_meetme)
        self.session.commit()

        meetme = MeetmeFeatures()
        meetme.meetmeid = meetmeid
        meetme.name = name
        meetme.confno = confno
        meetme.meetmeid = static_meetme.id

        self.session.add(meetme)
        self.session.commit()

        return meetme

    def test_get_one_result(self):
        meetme = self._insert_meetme(1, 'red', '9000')

        result = meetme_features_dao.get(meetme.id)

        self.assertEqual(result.id, meetme.id)

    def test_get_string_id(self):
        meetme = self._insert_meetme(1, 'red', '9000')

        result = meetme_features_dao.get(str(meetme.id))

        self.assertEqual(result.id, meetme.id)

    def test_get_no_result(self):
        self.assertRaises(LookupError, lambda: meetme_features_dao.get(1))

    def test_find_by_name(self):
        self._insert_meetme(1, 'red', '9000')
        self._insert_meetme(2, 'blue', '9001')

        meetme_red = meetme_features_dao.find_by_name('red')
        meetme_blue = meetme_features_dao.find_by_name('blue')

        self.assertEqual(meetme_red.name, 'red')
        self.assertEqual(meetme_blue.name, 'blue')

    def test_find_by_confno(self):
        red = self._insert_meetme(1, 'red', '9000')
        blue = self._insert_meetme(2, 'blue', '9001')

        red_id = meetme_features_dao.find_by_confno('9000')
        blue_id = meetme_features_dao.find_by_confno('9001')

        self.assertEqual(red_id, 1)
        self.assertEqual(blue_id, 2)

    def test_find_by_confno_no_conf(self):
        self.assertRaises(LookupError, meetme_features_dao.find_by_confno, '1234')

    def test_get_name(self):
        red = self._insert_meetme(1, 'red', '9000')

        result = meetme_features_dao.get_name(red.id)

        self.assertEqual(result, 'red')

    def test_has_pin_true(self):
        red = self._insert_meetme(1, 'red', '9000', '1234')

        result = meetme_features_dao.has_pin(red.id)

        self.assertTrue(result)

    def test_has_pin_false(self):
        red = self._insert_meetme(1, 'red', '9000')

        result = meetme_features_dao.has_pin(red.id)

        self.assertFalse(result)

    def test_has_pin_no_confroom(self):
        self.assertRaises(LookupError, meetme_features_dao.has_pin, 1)

    def test_get_configs(self):
        red = self._insert_meetme(1, 'red', '9000')
        blue = self._insert_meetme(2, 'blue', '9001', '1234')
        green = self._insert_meetme(3, 'green', '9002', '5555')

        result = meetme_features_dao.get_configs()

        expected = [('red', '9000', False),
                    ('blue', '9001', True),
                    ('green', '9002', True)]

        for config in expected:
            self.assertTrue(config in result)

    def test_get_config(self):
        self.assertRaises(LookupError, meetme_features_dao.get_config, 2)

        red = self._insert_meetme(1, 'red', '9000')
        blue = self._insert_meetme(2, 'blue', '9001', '1234')
        green = self._insert_meetme(3, 'green', '9002', '5555')

        result = meetme_features_dao.get_config(2)

        expected = ('blue', '9001', True)

        self.assertEqual(result, expected)
