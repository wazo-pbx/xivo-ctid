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


from xivo_cti.dao.alchemy.agentfeatures import AgentFeatures
from xivo_cti.dao.alchemy import dbconnection


class AgentFeaturesDAO(object):

    def __init__(self, session):
        self._session = session

    def agent_number(self, agentid):
        return self._get_one(agentid).number

    def agent_context(self, agentid):
        return self._get_one(agentid).context

    def agent_ackcall(self, agentid):
        return self._get_one(agentid).ackcall

    def agent_interface(self, id):
        return 'Agent/%s' % self._get_one(id).number

    def _get_one(self, id):
        res = self._session.query(AgentFeatures).filter(AgentFeatures.id == int(id))
        if res.count() == 0:
            raise LookupError('No such agent')
        return res[0]

    @classmethod
    def new_from_uri(cls, uri):
        connection = dbconnection.get_connection(uri)
        return cls(connection.get_session())
