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
from itertools import imap
from xivo_cti import xivo_ldap
from xivo_cti.directory.data_sources.directory_data_source import DirectoryDataSource


logger = logging.getLogger('ldap directory')

class LDAPDirectoryDataSource(DirectoryDataSource):
    def __init__(self, uri, key_mapping):
        self._uri = uri
        self._key_mapping = key_mapping
        self._map_fun = self._new_map_fun()
        self._xivo_ldap = None

    def lookup(self, string, fields, contexts=None):
        if string:
            ldap_filter = ['(%s=*%s*)' % (field, string) for field in fields]
            str_ldap_filter = '(|%s)' % ''.join(ldap_filter)
        else:
            return []

        ldap_attributes = []
        for src_key in self._key_mapping.itervalues():
            if isinstance(src_key, unicode):
                ldap_attributes.append(src_key.encode('UTF-8'))
            else:
                ldap_attributes.append(src_key)
        ldapid = self._try_connect()
        if ldapid.ldapobj is not None:
            try:
                results = ldapid.getldap(str_ldap_filter, ldap_attributes, string)
            except Exception, e:
                logger.warning('Error with LDAP request: %s', e)
                self._xivo_ldap = None
            else:
                if results is not None:
                    return imap(self._map_fun, results)
        return []

    def _try_connect(self):
        # Try to connect/reconnect to the LDAP if necessary
        if self._xivo_ldap is None:
            ldapid = xivo_ldap.xivo_ldap(self._uri)
            if ldapid.ldapobj is not None:
                self._xivo_ldap = ldapid
        else:
            ldapid = self._xivo_ldap
            if ldapid.ldapobj is None:
                self._xivo_ldap = None
        return ldapid

    def _new_map_fun(self):
        def aux(ldap_result):
            return dict((std_key, ldap_result[1][src_key][0]) for
                        (std_key, src_key) in self._key_mapping.iteritems() if
                        src_key in ldap_result[1])
        return aux

    @classmethod
    def new_from_contents(cls, ctid, contents):
        uri = contents['uri']
        key_mapping = cls._get_key_mapping(contents)
        return cls(uri, key_mapping)
