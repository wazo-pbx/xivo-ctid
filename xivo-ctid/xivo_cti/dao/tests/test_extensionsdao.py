#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2011  Avencall
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

from xivo_cti.dao.extensionsdao import ExtensionsDAO
from xivo_cti.dao.alchemy import dbconnection
from xivo_cti.dao.alchemy.base import Base
from xivo_cti.dao.alchemy.extension import Extension


class TestExtensionsDAO(unittest.TestCase):

    def setUp(self):
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        connection = dbconnection.get_connection('asterisk')

        Base.metadata.drop_all(connection.get_engine(), [Extension().__table__])
        Base.metadata.create_all(connection.get_engine(), [Extension().__table__])

        self.session = connection.get_session()

        self._insert_extens()

        self.session.commit()

    def tearDown(self):
        dbconnection.unregister_db_connection_pool()

    def _insert_extens(self):
        exten = Extension()
        exten.name = 'enablednd'
        exten.exten = '*25'
        self.session.add(exten)
        exten = Extension()
        exten.name = 'phoneprogfunckey'
        exten.exten = '_*735'
        self.session.add(exten)

    def test_exten_by_name(self):
        dao = ExtensionsDAO(self.session)

        enablednd = dao.exten_by_name('enablednd')
        phoneprogfunckey = dao.exten_by_name('phoneprogfunckey')

        self.assertEqual(enablednd, '*25')
        self.assertEqual(phoneprogfunckey, '_*735')
