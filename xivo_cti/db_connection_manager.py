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

import Queue

from xivo import anysql


class DbConnectionPool(object):
    '''Connection manager for DB connections.

    A single connection will be established for any given URI and a connection
    will not be shared by two processes at the same time. The with statement
    will be blocked if the connection is already in use.

    Usage:
        with DbConnectionPool(uri) as connection:
            connection['cur'].query(query)
            connection['conn'].commit()
    '''

    _pool = {}

    def __init__(self, db_uri):
        self._db_uri = db_uri
        if db_uri not in DbConnectionPool._pool:
            DbConnectionPool._pool[db_uri] = Queue.Queue()
            connection = {}
            connection['conn'] = anysql.connect_by_uri(db_uri)
            connection['cur'] = connection['conn'].cursor()
            DbConnectionPool._pool[db_uri].put(connection)

    def __enter__(self):
        return self.get()

    def __exit__(self, type, value, traceback):
        self.put()

    def get(self):
        self._connection = DbConnectionPool._pool[self._db_uri].get()
        return self._connection

    def put(self):
        DbConnectionPool._pool[self._db_uri].put(self._connection)
