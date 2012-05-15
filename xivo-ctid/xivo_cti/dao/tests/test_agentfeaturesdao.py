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

import unittest

from xivo_cti.dao.alchemy import dbconnection
from xivo_cti.dao.alchemy.agentfeatures import AgentFeatures
from xivo_cti.dao.alchemy.base import Base
from xivo_cti.dao.agentfeaturesdao import AgentFeaturesDAO


class TestAgentFeaturesDAO(unittest.TestCase):

    agent_number = '1234'
    agent_context = 'test'
    agent_ackcall = 'yes'

    def setUp(self):
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        connection = dbconnection.get_connection('asterisk')

        Base.metadata.drop_all(connection.get_engine(), [AgentFeatures.__table__])
        Base.metadata.create_all(connection.get_engine(), [AgentFeatures.__table__])

        self.session = connection.get_session()

        self.session.commit()
        self.session = connection.get_session()

        self.dao = AgentFeaturesDAO(self.session)

    def tearDown(self):
        dbconnection.unregister_db_connection_pool()

    def test_agent_number(self):
        agent_id = self._insert_agent()

        number = self.dao.agent_number(agent_id)

        self.assertEqual(number, self.agent_number)

    def test_agent_context(self):
        agent_id = self._insert_agent()

        context = self.dao.agent_context(agent_id)

        self.assertEqual(context, self.agent_context)

    def test_agent_ackcall(self):
        agent_id = self._insert_agent()

        ackcall = self.dao.agent_ackcall(agent_id)

        self.assertEqual(ackcall, self.agent_ackcall)

    def test_agent_number_unknown(self):
        self.assertRaises(LookupError, lambda: self.dao.agent_number(-1))

    def _insert_agent(self):
        agent = AgentFeatures()
        agent.numgroup = 6
        agent.number = self.agent_number
        agent.passwd = ''
        agent.context = self.agent_context
        agent.language = ''
        agent.ackcall = self.agent_ackcall

        self.session.add(agent)
        self.session.commit()

        return agent.id

    def test_agent_interface(self):
        agent_id = self._insert_agent()

        interface = self.dao.agent_interface(agent_id)

        self.assertEqual(interface, 'Agent/%s' % self.agent_number)
