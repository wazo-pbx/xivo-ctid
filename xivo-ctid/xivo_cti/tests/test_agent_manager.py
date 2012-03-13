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

from xivo_cti.agent_manager import AgentManager
from tests.mock import Mock
from xivo_cti.dao.alchemy import dbconnection
from xivo_cti.dao.alchemy.agentfeatures import AgentFeatures
from xivo_cti.dao.alchemy.userfeatures import UserFeatures
from xivo_cti.dao.alchemy.linefeatures import LineFeatures
from xivo_cti.dao.alchemy.base import Base
from xivo_cti.dao.userfeaturesdao import UserFeaturesDAO
from xivo_cti.dao.linefeaturesdao import LineFeaturesDAO
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.xivo_ami import AMIClass
from xivo_cti.dao.agentfeaturesdao import AgentFeaturesDAO


class TestAgentManager(unittest.TestCase):

    line_number = '1432'
    connected_user_id = 6

    def setUp(self):
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        connection = dbconnection.get_connection('asterisk')

        self.session = connection.get_session()

        Base.metadata.drop_all(connection.get_engine(), [LineFeatures.__table__])
        Base.metadata.create_all(connection.get_engine(), [LineFeatures.__table__])
        Base.metadata.drop_all(connection.get_engine(), [UserFeatures.__table__])
        Base.metadata.create_all(connection.get_engine(), [UserFeatures.__table__])

        self.agent_1_exten = '1000'

        self.agent_features_dao = AgentFeaturesDAO(self.session)
        self.user_features_dao = UserFeaturesDAO(self.session)
        self.line_features_dao = LineFeaturesDAO(self.session)

        self.agent_manager = AgentManager()
        self.agent_manager.agent_features_dao = self.agent_features_dao
        self.agent_manager.user_features_dao = self.user_features_dao
        self.agent_manager.line_features_dao = self.line_features_dao

    def tearDown(self):
        dbconnection.unregister_db_connection_pool()

    def test_log_agent(self):
        self.agent_manager.agent_call_back_login = Mock()

        agent = self._insert_agent()

        self._insert_line_with_number(self.agent_1_exten)

        self.agent_manager.agent_call_back_login = Mock()

        self.agent_manager.log_agent(self.connected_user_id, agent.id, self.agent_1_exten)

        self.agent_manager.agent_call_back_login.assert_called_once_with(agent.number,
                                                                         self.agent_1_exten,
                                                                         agent.context,
                                                                         agent.ackcall != 'no')

    def test_log_agent_no_number(self):
        self.agent_manager.agent_call_back_login = Mock()
        agent = self._insert_agent()
        user_id = self._insert_user_with_agent(agent.id)
        self._insert_line_with_user(user_id)

        self.agent_manager.log_agent(self.connected_user_id, agent.id)

        self.agent_manager.agent_call_back_login.assert_called_once_with(agent.number,
                                                                         self.line_number,
                                                                         agent.context,
                                                                         agent.ackcall != 'no')

    def test_find_agent_exten(self):
        agent = self._insert_agent()
        user_id = self._insert_user_with_agent(agent.id)
        self._insert_line_with_user(user_id)

        extens = self.agent_manager.find_agent_exten(agent.id)

        self.assertEqual(extens[0], self.line_number)

    def test_agent_callback_login(self):
        number, exten, context, ackcall = '1000', '1234', 'test', False
        ami = Mock(AMIClass)
        self.agent_manager.ami = ami

        self.agent_manager.agent_call_back_login(number,
                                                 exten,
                                                 context,
                                                 ackcall)

        ami.agentcallbacklogin.assert_called_once_with(number, exten, context, ackcall)

    def test_agent_special_me(self):
        self.agent_manager.agent_call_back_login = Mock()
        agent = self._insert_agent()
        user_id = self._insert_user_with_agent(agent.id)
        self._insert_line_with_user(user_id)

        self.agent_manager.log_agent(user_id, 'agent:special:me')

        self.agent_manager.agent_call_back_login.assert_called_once_with(agent.number,
                                                                         self.line_number,
                                                                         agent.context,
                                                                         agent.ackcall != 'no')

    def _insert_line_with_number(self, number):
        line = LineFeatures()
        line.iduserfeatures = 0
        line.protocolid = 1
        line.provisioningid = 0
        line.name = 'ix8pa'
        line.context = 'test_context'
        line.number = number
        self.session.add(line)

        self.session.commit()

    def _insert_line_with_user(self, user_id):
        line = LineFeatures()
        line.iduserfeatures = user_id
        line.protocolid = 1
        line.provisioningid = 0
        line.name = 'ix8pa'
        line.context = 'test_context'
        line.number = self.line_number
        self.session.add(line)

        self.session.commit()

    def _insert_user_with_agent(self, agent_id):
        user = UserFeatures()
        user.firstname = 'test_agent'
        user.agentid = agent_id
        self.session.add(user)
        self.session.commit()

        return user.id

    def _insert_agent(self):
        agent = AgentFeatures()
        agent.agentid = 44
        agent.numgroup = 6
        agent.number = '1234'
        agent.passwd = ''
        agent.context = 'test_context'
        agent.language = ''

        self.session.add(agent)
        self.session.commit()

        return agent
