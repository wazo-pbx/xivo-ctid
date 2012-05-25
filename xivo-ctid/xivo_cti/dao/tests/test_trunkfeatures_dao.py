#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the
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

from xivo_cti.dao.alchemy.trunkfeatures import TrunkFeatures
from xivo_cti.dao.alchemy.usersip import UserSIP
from xivo_cti.dao.alchemy.useriax import UserIAX
from xivo_cti.dao.trunkfeaturesdao import TrunkFeaturesDAO
from xivo_cti.dao.alchemy import dbconnection
from xivo_cti.dao.alchemy.base import Base

class TrunkFeaturesDAOTestCase(unittest.TestCase):

    def setUp(self):
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        connection = dbconnection.get_connection('asterisk')

        Base.metadata.drop_all(connection.get_engine(), [TrunkFeatures.__table__])
        Base.metadata.create_all(connection.get_engine(), [TrunkFeatures.__table__])

        Base.metadata.drop_all(connection.get_engine(), [UserSIP.__table__])
        Base.metadata.create_all(connection.get_engine(), [UserSIP.__table__])

        Base.metadata.drop_all(connection.get_engine(), [UserIAX.__table__])
        Base.metadata.create_all(connection.get_engine(), [UserIAX.__table__])

        self.session = connection.get_session()

        self.session.commit()
        self.session = connection.get_session()

        self.dao = TrunkFeaturesDAO(self.session)

    def tearDown(self):
        dbconnection.unregister_db_connection_pool()


    def test_find_by_proto_name_sip(self):
        trunk_name = 'my_trunk'

        trunk = TrunkFeatures()
        trunk.protocolid = 5436
        trunk.protocol = 'sip'

        usersip = UserSIP()
        usersip.id = trunk.protocolid
        usersip.name = trunk_name
        usersip.type = 'peer'

        self.session.add(trunk)
        self.session.add(usersip)

        self.session.commit()

        result = self.dao.find_by_proto_name('sip', trunk_name)

        self.assertEqual(result, trunk.id)

    def test_find_by_proto_name_iax(self):
        trunk_name = 'my_trunk'

        trunk = TrunkFeatures()
        trunk.protocolid = 5454
        trunk.protocol = 'iax'

        useriax = UserIAX()
        useriax.id = trunk.protocolid
        useriax.name = trunk_name
        useriax.type = 'peer'

        self.session.add(trunk)
        self.session.add(useriax)

        self.session.commit()

        result = self.dao.find_by_proto_name('iax', trunk_name)

        self.assertEqual(result, trunk.id)

    def test_null_input(self):
        self.assertRaises(ValueError, self.dao.find_by_proto_name, None, 'my_trunk')

    def test_get_ids(self):
        trunk1 = TrunkFeatures()
        trunk1.protocolid = '1234'
        trunk1.protocol = 'sip'

        trunk2 = TrunkFeatures()
        trunk2.protocolid = '4321'
        trunk2.protocol = 'iax'

        trunk3 = TrunkFeatures()
        trunk3.protocolid = '5678'
        trunk3.protocol = 'sip'

        map(self.session.add, [trunk1, trunk2, trunk3])
        self.session.commit()

        expected = sorted([trunk1.id, trunk2.id, trunk3.id])
        result = sorted(self.dao.get_ids())

        self.assertEqual(expected, result)

    def test_get_ids_empty(self):
        result = self.dao.get_ids()
        self.assertEqual([], result)
