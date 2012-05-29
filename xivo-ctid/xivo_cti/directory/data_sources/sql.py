# -*- coding: utf-8 -*-

# XiVO CTI Server
# Copyright (C) 2009-2012  Avencall
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

import logging
from itertools import izip
from xivo_cti import db_connection_manager
from xivo_cti.directory.data_sources.directory_data_source import DirectoryDataSource

logger = logging.getLogger('sql directory')

class SQLDirectoryDataSource(DirectoryDataSource):
    def __init__(self, db_uri, key_mapping):
        self._db_uri = db_uri
        self._key_mapping = key_mapping
        self._map_fun = self._new_map_fun()

    def lookup(self, string, fields, contexts=None):
        # handle when fields is empty to simplify implementation
        if not fields:
            logger.warning('No requested fields')
            return []

        table, test_columns = self._get_table_and_columns_from_fields(fields)
        request_beg = 'SELECT ${columns} FROM %s WHERE ' % table
        request_end = ' OR '.join('%s LIKE %%s' % column for column in test_columns)
        request = request_beg + request_end
        params = ('%' + string + '%',) * len(test_columns)
        columns = tuple(self._key_mapping.itervalues())

        conn_mgr = db_connection_manager.DbConnectionPool(self._db_uri)
        connection = conn_mgr.get()
        try:
            cursor = connection['cur']
            cursor.query(request, columns, params)
            def generator():
                try:
                    while True:
                        row = cursor.fetchone()
                        if row is None:
                            break
                        yield self._map_fun(row)
                finally:
                    conn_mgr.put()
            return generator()
        except Exception:
            conn_mgr.put()
            raise

    def _get_table_and_columns_from_fields(self, fields):
        # Return a tuple (table id, list of column ids)
        tables = set()
        columns = set()
        for field in fields:
            table, column = field.split('.', 1)
            tables.add(table)
            columns.add(column)
        if len(tables) != 1:
            raise ValueError('fields must reference exactly 1 table: %s' % tables)
        return tables.pop(), list(columns)

    def _new_map_fun(self):
        def aux(row):
            return dict(izip(self._key_mapping, row))
        return aux

    @classmethod
    def new_from_contents(cls, ctid, contents):
        db_uri = contents['uri']
        key_mapping = cls._get_key_mapping(contents)
        return cls(db_uri, key_mapping)
