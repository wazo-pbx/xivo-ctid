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

from xivo_cti.services.agent_service_manager import AgentServiceManager
from xivo_cti.services.queue_member.manager import QueueMemberManager
from xivo_cti.services.agent_executor import AgentExecutor


class TestAgentServiceManager(unittest.TestCase):

    line_number = '1432'
    connected_user_id = 6

    def setUp(self):
        self.agent_1_exten = '1000'
        agent_executor = Mock(AgentExecutor)
        queue_member_manager = Mock(QueueMemberManager)
        self.agent_manager = AgentServiceManager(agent_executor,
                                                 queue_member_manager)

    @patch('xivo_dao.line_dao.is_phone_exten')
    @patch('xivo_dao.line_dao.number')
    @patch('xivo_dao.line_dao.find_line_id_by_user_id')
    @patch('xivo_dao.agent_dao.agent_context')
    @patch('xivo_dao.user_dao.find_by_agent_id')
    @patch('xivo_dao.user_dao.agent_id')
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

    @patch('xivo_dao.line_dao.is_phone_exten')
    @patch('xivo_dao.line_dao.number')
    @patch('xivo_dao.line_dao.find_line_id_by_user_id')
    @patch('xivo_dao.agent_dao.agent_context')
    @patch('xivo_dao.user_dao.find_by_agent_id')
    @patch('xivo_dao.user_dao.agent_id')
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

    @patch('xivo_dao.line_dao.is_phone_exten')
    @patch('xivo_dao.line_dao.number')
    @patch('xivo_dao.line_dao.find_line_id_by_user_id')
    @patch('xivo_dao.agent_dao.agent_context')
    @patch('xivo_dao.user_dao.find_by_agent_id')
    @patch('xivo_dao.user_dao.agent_id')
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

    @patch('xivo_dao.line_dao.number')
    @patch('xivo_dao.line_dao.find_line_id_by_user_id')
    @patch('xivo_dao.user_dao.find_by_agent_id')
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

        self.agent_manager.agent_executor.login.assert_called_once_with(number, exten, context)

    def test_logoff(self):
        agent_id = 44

        self.agent_manager.logoff(agent_id)

        self.agent_manager.agent_executor.logoff.assert_called_once_with(agent_id)

    def test_add_agent_to_queue(self):
        agent_id = 42
        queue_id = 1

        self.agent_manager.add_agent_to_queue(agent_id, queue_id)

        self.agent_manager.agent_executor.add_to_queue.assert_called_once_with(agent_id, queue_id)

    def test_remove_agent_from_queue(self):
        agent_id = 42
        queue_id = 1

        self.agent_manager.remove_agent_from_queue(agent_id, queue_id)

        self.agent_manager.agent_executor.remove_from_queue.assert_called_once_with(agent_id, queue_id)

    @patch('xivo_dao.queue_features_dao.queue_name')
    def test_pause_agent_on_queue(self, mock_queue_name):
        agent_id = 42
        agent_interface = 'SIP/abcdef'
        queue_id = 1
        queue_name = 'foobar'
        self.agent_manager._get_agent_interface = Mock()
        self.agent_manager._get_agent_interface.return_value = agent_interface
        mock_queue_name.return_value = queue_name

        self.agent_manager.pause_agent_on_queue(agent_id, queue_id)

        self.agent_manager.agent_executor.pause_on_queue.assert_called_once_with(agent_interface, queue_name)

    def test_pause_agent_on_all_queues(self):
        agent_id = 42
        agent_interface = 'SIP/abcdef'
        self.agent_manager._get_agent_interface = Mock()
        self.agent_manager._get_agent_interface.return_value = agent_interface

        self.agent_manager.pause_agent_on_all_queues(agent_id)

        self.agent_manager.agent_executor.pause_on_all_queues.assert_called_once_with(agent_interface)

    @patch('xivo_dao.queue_features_dao.queue_name')
    def test_unpause_agent_on_queue(self, mock_queue_name):
        agent_id = 42
        agent_interface = 'SIP/abcdef'
        queue_id = 1
        queue_name = 'foobar'
        self.agent_manager._get_agent_interface = Mock()
        self.agent_manager._get_agent_interface.return_value = agent_interface
        mock_queue_name.return_value = queue_name

        self.agent_manager.unpause_agent_on_queue(agent_id, queue_id)

        self.agent_manager.agent_executor.unpause_on_queue.assert_called_once_with(agent_interface, queue_name)

    def test_unpause_agent_on_all_queues(self):
        agent_id = 42
        agent_interface = 'SIP/abcdef'
        self.agent_manager._get_agent_interface = Mock()
        self.agent_manager._get_agent_interface.return_value = agent_interface

        self.agent_manager.unpause_agent_on_all_queues(agent_id)

        self.agent_manager.agent_executor.unpause_on_all_queues.assert_called_once_with(agent_interface)

    @patch('xivo_dao.agent_dao.agent_interface')
    def test_set_presence(self, mock_agent_interface):
        presence = 'disconnected'
        agent_id = 34
        agent_member_name = 'Agent/1234'
        mock_agent_interface.return_value = agent_member_name

        self.agent_manager.set_presence(agent_id, presence)

        self.agent_manager.agent_executor.log_presence.assert_called_once_with(agent_member_name, presence)
