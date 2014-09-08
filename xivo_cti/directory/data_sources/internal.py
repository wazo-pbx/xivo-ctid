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

import logging

from itertools import izip
from xivo_cti import db_connection_manager, cti_config
from xivo_cti.ioc.context import context as cti_context
from xivo_dird.directory.data_sources.directory_data_source import DirectoryDataSource


logger = logging.getLogger('internal directory')


class InternalDirectoryDataSource(DirectoryDataSource):

    def __init__(self, key_mapping):
        self._key_mapping = key_mapping
        self._map_fun = self._new_map_fun()

    def lookup(self, string, fields, contexts=None):
        # handle when fields is empty to simplify implementation
        if not fields:
            logger.warning('No requested fields')
            return []

        test_columns = fields
        request_beg = ('SELECT ${columns} FROM userfeatures '
                       'LEFT JOIN user_line '
                       'ON userfeatures.id = user_line.user_id '
                       'LEFT JOIN extensions '
                       "ON extensions.type = 'user' AND userfeatures.id = CAST(extensions.typeval as integer) "
                       'WHERE ')
        request_end = ' OR '.join('%s ILIKE %%s' % column for column in test_columns)
        if cti_context.get('cti_config').part_context():
            if contexts:
                request_contexts = ' OR '.join("extensions.context = '%s'" % context for context in contexts)
            else:
                request_contexts = '1 = 0'
            request = request_beg + '(' + request_end + ') and (' + request_contexts + ')'
        else:
            request = request_beg + request_end
        params = ('%' + string + '%',) * len(test_columns)
        columns = tuple(self._key_mapping.itervalues())

        conn_mgr = db_connection_manager.DbConnectionPool(cti_config.DB_URI)
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

    def _new_map_fun(self):
        def aux(row):
            return dict(izip(self._key_mapping, row))
        return aux

    @classmethod
    def new_from_contents(cls, ctid, contents):
        key_mapping = cls._get_key_mapping(contents)
        return cls(key_mapping)
