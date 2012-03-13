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

from xivo_cti.dao.alchemy.linefeatures import LineFeatures
from xivo_cti.dao.alchemy import dbconnection


class LineFeaturesDAO(object):

    def __init__(self, session):
        self._session = session

    def find_by_user(self, user_id):
        res = self._session.query(LineFeatures).filter(LineFeatures.iduserfeatures == int(user_id))
        return [line.id for line in res]

    def number(self, line_id):
        res = self._session.query(LineFeatures).filter(LineFeatures.id == line_id)
        if res.count() == 0:
            raise LookupError
        else:
            return res[0].number

    def is_phone_exten(self, exten):
        return self._session.query(LineFeatures).filter(LineFeatures.number == exten).count() > 0

    @classmethod
    def new_from_uri(cls, uri):
        connection = dbconnection.get_connection(uri)
        return cls(connection.get_session())
