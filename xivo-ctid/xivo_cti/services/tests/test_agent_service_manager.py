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

from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_cti.services.agent_service_manager import AgentServiceManager
from xivo_cti.services.agent_executor import AgentExecutor
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_cti.dao.innerdatadao import InnerdataDAO


class TestAgentServiceManager(unittest.TestCase):

    line_number = '1432'
    connected_user_id = 6
    tables = [LineFeatures, UserFeatures, AgentFeatures]

    def setUp(self):
        self.agent_1_exten = '1000'

        self.agent_executor = Mock(AgentExecutor)
        self.innerdata_dao = Mock(InnerdataDAO)
        self.agent_manager = AgentServiceManager(self.agent_executor,
                                                 self.innerdata_dao)

    @patch('xivo_dao.linefeatures_dao.is_phone_exten')
    @patch('xivo_dao.linefeatures_dao.number')
    @patch('xivo_dao.linefeatures_dao.find_line_id_by_user_id')
    @patch('xivo_dao.agentfeatures_dao.agent_context')
    @patch('xivo_dao.userfeatures_dao.find_by_agent_id')
    @patch('xivo_dao.userfeatures_dao.agent_id')
    @patch('xivo_cti.tools.idconverter.IdConverter.xid_to_id')
    def test_on_cti_agent_login(self,
                                mock_id_converter,
                                mock_agent_id,
                                mock_find_by_agent_id,
                                mock_agent_context,
                                mock_find_line_id_by_user_id,
                                mock_number,
                                mock_is_phone_exten):
        user_id = 10
        agent_id = 11
        line_id = 12
        agent_context = 'test_context'
        mock_id_converter.return_value = agent_id
        mock_agent_id.return_value = agent_id
        mock_find_by_agent_id.return_value = [user_id]
        mock_find_line_id_by_user_id.return_value = [line_id]
        mock_number.return_value = self.line_number
        mock_is_phone_exten.return_value = True
        mock_agent_context.return_value = agent_context
        self.agent_manager.login = Mock()

        self.agent_manager.on_cti_agent_login(self.connected_user_id, agent_id, self.agent_1_exten)

        self.agent_manager.login.assert_called_once_with(agent_id, self.agent_1_exten, agent_context)

    @patch('xivo_cti.tools.idconverter.IdConverter.xid_to_id')
    def test_on_cti_agent_logout(self, mock_id_converter):
        agent_id = 11
        mock_id_converter.return_value = agent_id
        self.agent_manager.logoff = Mock()

        self.agent_manager.on_cti_agent_logout(self.connected_user_id, agent_id)

        self.agent_manager.logoff.assert_called_once_with(agent_id)

    @patch('xivo_dao.linefeatures_dao.is_phone_exten')
    @patch('xivo_dao.linefeatures_dao.number')
    @patch('xivo_dao.linefeatures_dao.find_line_id_by_user_id')
    @patch('xivo_dao.agentfeatures_dao.agent_context')
    @patch('xivo_dao.userfeatures_dao.find_by_agent_id')
    @patch('xivo_dao.userfeatures_dao.agent_id')
    @patch('xivo_cti.tools.idconverter.IdConverter.xid_to_id')
    def test_on_cti_agent_login_no_number(self,
                                          mock_id_converter,
                                          mock_agent_id,
                                          mock_find_by_agent_id,
                                          mock_agent_context,
                                          mock_find_line_id_by_user_id,
                                          mock_number,
                                          mock_is_phone_exten):
        user_id = 10
        agent_id = 11
        line_id = 12
        agent_context = 'test_context'
        mock_id_converter.return_value = agent_id
        mock_agent_id.return_value = agent_id
        mock_find_by_agent_id.return_value = [user_id]
        mock_find_line_id_by_user_id.return_value = [line_id]
        mock_number.return_value = self.line_number
        mock_is_phone_exten.return_value = True
        mock_agent_context.return_value = agent_context
        self.agent_manager.login = Mock()

        self.agent_manager.on_cti_agent_login(self.connected_user_id, agent_id)

        self.agent_manager.login.assert_called_once_with(agent_id, self.line_number, agent_context)

    @patch('xivo_dao.linefeatures_dao.is_phone_exten')
    @patch('xivo_dao.linefeatures_dao.number')
    @patch('xivo_dao.linefeatures_dao.find_line_id_by_user_id')
    @patch('xivo_dao.agentfeatures_dao.agent_context')
    @patch('xivo_dao.userfeatures_dao.find_by_agent_id')
    @patch('xivo_dao.userfeatures_dao.agent_id')
    @patch('xivo_cti.tools.idconverter.IdConverter.xid_to_id')
    def test_agent_special_me(self,
                              mock_id_converter,
                              mock_agent_id,
                              mock_find_by_agent_id,
                              mock_agent_context,
                              mock_find_line_id_by_user_id,
                              mock_number,
                              mock_is_phone_exten):
        user_id = 12
        agent_id = 44
        agent_context = 'test_context'
        mock_id_converter.return_value = agent_id
        mock_agent_id.return_value = agent_id
        mock_find_by_agent_id.return_value = [user_id]
        mock_find_line_id_by_user_id.return_value = [13]
        mock_number.return_value = self.line_number
        mock_is_phone_exten.return_value = True
        mock_agent_context.return_value = agent_context
        self.agent_manager.login = Mock()

        self.agent_manager.on_cti_agent_login(user_id, 'agent:special:me')

        self.agent_manager.login.assert_called_once_with(agent_id, self.line_number, agent_context)

    @patch('xivo_dao.linefeatures_dao.number')
    @patch('xivo_dao.linefeatures_dao.find_line_id_by_user_id')
    @patch('xivo_dao.userfeatures_dao.find_by_agent_id')
    def test_find_agent_exten(self,
                              mock_find_by_agent_id,
                              mock_find_line_id_by_user_id,
                              mock_number):
        agent_id = 11
        mock_find_by_agent_id.return_value = [12]
        mock_find_line_id_by_user_id.return_value = [13]
        mock_number.return_value = self.line_number

        extens = self.agent_manager.find_agent_exten(agent_id)

        self.assertEqual(extens[0], self.line_number)

    def test_login(self):
        number, exten, context = '1000', '1234', 'test'

        self.agent_manager.login(number, exten, context)

        self.agent_executor.login.assert_called_once_with(number, exten, context)

    def test_logoff(self):
        agent_id = 44

        self.agent_manager.logoff(agent_id)

        self.agent_executor.logoff.assert_called_once_with(agent_id)

    @patch('xivo_dao.agentfeatures_dao.agent_interface')
    def test_queue_add(self, mock_agent_interface):
        queue_name = 'accueil'
        agent_id = 12
        agent_interface = 'Agent/1234'
        mock_agent_interface.return_value = agent_interface

        self.agent_manager.queueadd(queue_name, agent_id)

        self.agent_executor.queue_add.assert_called_once_with(queue_name, agent_interface, False, '')

    @patch('xivo_dao.agentfeatures_dao.agent_interface')
    def test_queue_remove(self, mock_agent_interface):
        queue_name = 'accueil'
        agent_id = 34
        agent_interface = 'Agent/1234'
        mock_agent_interface.return_value = agent_interface

        self.agent_manager.queueremove(queue_name, agent_id)

        self.agent_executor.queue_remove.assert_called_once_with(queue_name, agent_interface)

    @patch('xivo_dao.agentfeatures_dao.agent_interface')
    def test_queue_pause_all(self, mock_agent_interface):
        agent_id = 34
        agent_interface = 'Agent/1234'
        mock_agent_interface.return_value = agent_interface

        self.agent_manager.queuepause_all(agent_id)

        self.agent_executor.queues_pause.assert_called_once_with('Agent/1234')

    @patch('xivo_dao.agentfeatures_dao.agent_interface')
    def test_queue_unpause_all(self, mock_agent_interface):
        agent_id = 34
        agent_interface = 'Agent/1234'
        mock_agent_interface.return_value = agent_interface

        self.agent_manager.queueunpause_all(agent_id)

        self.agent_executor.queues_unpause(agent_interface)

    @patch('xivo_dao.agentfeatures_dao.agent_interface')
    def test_queue_pause(self, mock_agent_interface):
        queue_name = 'accueil'
        agent_id = 34
        agent_interface = 'Agent/1234'
        mock_agent_interface.return_value = agent_interface

        self.agent_manager.queuepause(queue_name, agent_id)

        self.agent_executor.queue_pause.assert_called_once_with(queue_name, agent_interface)

    @patch('xivo_dao.agentfeatures_dao.agent_interface')
    def test_queue_unpause(self, mock_agent_interface):
        queue_name = 'accueil'
        agent_id = 34
        agent_interface = 'Agent/1234'
        mock_agent_interface.return_value = agent_interface

        self.agent_manager.queueunpause(queue_name, agent_id)

        self.agent_executor.queue_unpause(queue_name, agent_interface)

    @patch('xivo_dao.agentfeatures_dao.agent_interface')
    def test_set_presence(self, mock_agent_interface):
        presence = 'disconnected'
        agent_id = 34
        agent_interface = 'Agent/1234'
        mock_agent_interface.return_value = agent_interface

        self.agent_manager.set_presence(agent_id, presence)

        self.agent_executor.log_presence.assert_called_once_with(agent_interface, presence)
