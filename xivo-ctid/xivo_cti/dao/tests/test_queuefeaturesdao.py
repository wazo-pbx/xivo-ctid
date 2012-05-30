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

from xivo_cti.dao.tests import test_dao
from xivo_cti.dao.queue_features_dao import QueueFeaturesDAO
from xivo_cti.dao.alchemy import dbconnection
from xivo_cti.dao.alchemy.queuefeatures import QueueFeatures


class TestQueueFeaturesDAO(test_dao.DAOTestCase):

    required_tables = [QueueFeatures.__table__]

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

        self.dao = QueueFeaturesDAO(self.session)

    def tearDown(self):
        dbconnection.unregister_db_connection_pool()

    def test_id_from_name(self):
        queue = QueueFeatures()
        queue.name = 'test_queue'
        queue.displayname = 'Queue Test'

        self.session.add(queue)
        self.session.commit()

        result = self.dao.id_from_name(queue.name)

        self.assertEqual(result, queue.id)

    def test_queue_name(self):
        queue = QueueFeatures()
        queue.name = 'my_queue'
        queue.displayname = 'My Queue'

        self.session.add(queue)
        self.session.commit()

        result = self.dao.queue_name(queue.id)

        self.assertEquals(result, 'my_queue')

    def test_is_a_queue(self):
        self.assertFalse(self.dao.is_a_queue('not_a_queue'))

        queue = QueueFeatures()
        queue.name = 'a_queue'
        queue.displayname = 'My queue'

        self.session.add(queue)
        self.session.commit()

        self.assertTrue(self.dao.is_a_queue('a_queue'))
