# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from mock import Mock, patch

from xivo_dao.agentfeaturesdao import AgentFeaturesDAO
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.linefeaturesdao import LineFeaturesDAO
from xivo_cti.services.agent_service_manager import AgentServiceManager
from xivo_cti.services.agent_executor import AgentExecutor
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_cti.dao.innerdatadao import InnerdataDAO
from xivo_cti.dao.userfeaturesdao import UserFeaturesDAO


class TestAgentServiceManager(unittest.TestCase):

    line_number = '1432'
    connected_user_id = 6
    tables = [LineFeatures, UserFeatures, AgentFeatures]

    def setUp(self):
        self.agent_1_exten = '1000'

        self.user_features_dao = Mock(UserFeaturesDAO)
        self.line_features_dao = Mock(LineFeaturesDAO)
        self.agent_features_dao = Mock(AgentFeaturesDAO)

        self.agent_executor = Mock(AgentExecutor)
        self.innerdata_dao = Mock(InnerdataDAO)
        self.agent_manager = AgentServiceManager(self.agent_executor,
                                                 self.agent_features_dao,
                                                 self.innerdata_dao,
                                                 self.line_features_dao,
                                                 self.user_features_dao)

    @patch('xivo_cti.tools.idconverter.IdConverter.xid_to_id')
    def test_log_agent(self, mock_id_converter):
        user_id = 10
        agent_id = 11
        line_id = 12
        agent_number = '1234'
        agent_context = 'test_context'
        mock_id_converter.return_value = agent_id
        self.user_features_dao.agent_id.return_value = agent_id
        self.user_features_dao.find_by_agent_id.return_value = [user_id]
        self.line_features_dao.find_line_id_by_user_id.return_value = [line_id]
        self.line_features_dao.number.return_value = self.line_number
        self.line_features_dao.is_phone_exten.return_value = True
        self.agent_features_dao.agent_number.return_value = agent_number
        self.agent_features_dao.agent_context.return_value = agent_context
        self.agent_manager.agent_call_back_login = Mock()

        self.agent_manager.log_agent(self.connected_user_id, agent_id, self.agent_1_exten)

        self.agent_manager.agent_call_back_login.assert_called_once_with(agent_number,
                                                                         self.agent_1_exten,
                                                                         agent_context)

    @patch('xivo_cti.tools.idconverter.IdConverter.xid_to_id')
    def test_log_agent_no_number(self, mock_id_converter):
        user_id = 10
        agent_id = 11
        line_id = 12
        agent_number = '1234'
        agent_context = 'test_context'
        mock_id_converter.return_value = agent_id
        self.user_features_dao.agent_id.return_value = agent_id
        self.user_features_dao.find_by_agent_id.return_value = [user_id]
        self.line_features_dao.find_line_id_by_user_id.return_value = [line_id]
        self.line_features_dao.number.return_value = self.line_number
        self.line_features_dao.is_phone_exten.return_value = True
        self.agent_features_dao.agent_number.return_value = agent_number
        self.agent_features_dao.agent_context.return_value = agent_context
        self.agent_manager.agent_call_back_login = Mock()

        self.agent_manager.log_agent(self.connected_user_id, agent_id)

        self.agent_manager.agent_call_back_login.assert_called_once_with(agent_number,
                                                                         self.line_number,
                                                                         agent_context)

    def test_find_agent_exten(self):
        agent_id = 11
        self.user_features_dao.find_by_agent_id.return_value = [12]
        self.line_features_dao.find_line_id_by_user_id.return_value = [13]
        self.line_features_dao.number.return_value = self.line_number

        extens = self.agent_manager.find_agent_exten(agent_id)

        self.assertEqual(extens[0], self.line_number)

    def test_agent_callback_login(self):
        number, exten, context = '1000', '1234', 'test'

        self.agent_manager.agent_call_back_login(number,
                                                 exten,
                                                 context)

        self.agent_executor.agentcallbacklogin.assert_called_once_with(number, exten, context)

    @patch('xivo_cti.tools.idconverter.IdConverter.xid_to_id')
    def test_agent_special_me(self, mock_id_converter):
        user_id = 12
        agent_number = '1234'
        agent_context = 'test_context'
        mock_id_converter.return_value = 44
        self.user_features_dao.agent_id.return_value = 44
        self.user_features_dao.find_by_agent_id.return_value = [user_id]
        self.line_features_dao.find_line_id_by_user_id.return_value = [13]
        self.line_features_dao.number.return_value = self.line_number
        self.line_features_dao.is_phone_exten.return_value = True
        self.agent_features_dao.agent_number.return_value = agent_number
        self.agent_features_dao.agent_context.return_value = agent_context
        self.agent_manager.agent_call_back_login = Mock()

        self.agent_manager.log_agent(user_id, 'agent:special:me')

        self.agent_manager.agent_call_back_login.assert_called_once_with(agent_number,
                                                                         self.line_number,
                                                                         agent_context)

    def test_logoff(self):
        agent_id = 44
        agent_number = '1234'
        self.agent_features_dao.agent_number.return_value = agent_number

        self.agent_manager.logoff(agent_id)

        self.agent_executor.logoff.assert_called_once_with(agent_number)

    def test_queue_add(self):
        queue_name = 'accueil'
        agent_id = 12
        agent_interface = 'Agent/1234'
        self.agent_features_dao.agent_interface.return_value = agent_interface

        self.agent_manager.queueadd(queue_name, agent_id)

        self.agent_executor.queue_add.assert_called_once_with(queue_name, agent_interface, False, '')

    def test_queue_remove(self):
        queue_name = 'accueil'
        agent_id = 34
        agent_interface = 'Agent/1234'
        self.agent_features_dao.agent_interface.return_value = agent_interface

        self.agent_manager.queueremove(queue_name, agent_id)

        self.agent_executor.queue_remove.assert_called_once_with(queue_name, agent_interface)

    def test_queue_pause_all(self):
        agent_id = 34
        agent_interface = 'Agent/1234'
        self.agent_features_dao.agent_interface.return_value = agent_interface

        self.agent_manager.queuepause_all(agent_id)

        self.agent_executor.queues_pause.assert_called_once_with('Agent/1234')

    def test_queue_unpause_all(self):
        agent_id = 34
        agent_interface = 'Agent/1234'
        self.agent_features_dao.agent_interface.return_value = agent_interface

        self.agent_manager.queueunpause_all(agent_id)

        self.agent_executor.queues_unpause(agent_interface)

    def test_queue_pause(self):
        queue_name = 'accueil'
        agent_id = 34
        agent_interface = 'Agent/1234'
        self.agent_features_dao.agent_interface.return_value = agent_interface

        self.agent_manager.queuepause(queue_name, agent_id)

        self.agent_executor.queue_pause.assert_called_once_with(queue_name, agent_interface)

    def test_queue_unpause(self):
        queue_name = 'accueil'
        agent_id = 34
        agent_interface = 'Agent/1234'
        self.agent_features_dao.agent_interface.return_value = agent_interface

        self.agent_manager.queueunpause(queue_name, agent_id)

        self.agent_executor.queue_unpause(queue_name, agent_interface)

    def test_set_presence(self):
        presence = 'disconnected'
        agent_id = 34
        agent_interface = 'Agent/1234'
        self.agent_features_dao.agent_interface.return_value = agent_interface

        self.agent_manager.set_presence(agent_id, presence)

        self.agent_executor.log_presence.assert_called_once_with(agent_interface, presence)
