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

from xivo_cti.dao.alchemy.phonefunckey import PhoneFunckey
from xivo_cti.dao.alchemy import dbconnection

import logging

logger = logging.getLogger('PhoneFunckeyDAO    ')


class PhoneFunckeyDAO(object):

    def __init__(self, session):
        self._session = session

    def get_dest_unc(self, user_id):
        extens = (self._session.query(PhoneFunckey.exten)
                    .filter(PhoneFunckey.iduserfeatures == user_id)
                    .filter(PhoneFunckey.typevalextenumbers == 'fwdunc'))
        return extens[0][0] if extens else ''

    @classmethod
    def new_from_uri(cls, uri):
        connection = dbconnection.get_connection(uri)
        return cls(connection.get_session())
