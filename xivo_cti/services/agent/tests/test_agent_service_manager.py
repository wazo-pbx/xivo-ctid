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

import unittest
from mock import Mock, patch

from xivo_dao.alchemy.userfeatures import UserFeatures as User

from xivo_cti.exception import ExtensionInUseError, NoSuchExtensionError
from xivo_cti.services.agent.manager import AgentServiceManager
from xivo_cti.services.agent.executor import AgentExecutor


class TestAgentServiceManager(unittest.TestCase):

    line_number = '1432'
    connected_user_id = 6

    def setUp(self):
        self.agent_1_exten = '1000'
        self.agent_executor = Mock(AgentExecutor)
        self.ami = Mock()
        self.agent_manager = AgentServiceManager(self.agent_executor,
                                                 self.ami)

    @patch('xivo_dao.user_line_dao.is_phone_exten')
    @patch('xivo_dao.agent_dao.agent_context')
    @patch('xivo_dao.resources.user.dao')
    @patch('xivo_cti.tools.idconverter.IdConverter.xid_to_id')
    def test_on_cti_agent_login(self,
                                mock_id_converter,
                                mock_user_dao,
                                mock_agent_context,
                                mock_is_phone_exten):
        agent_id = 11
        agent_context = 'test_context'
        mock_id_converter.return_value = agent_id
        mock_user_dao.get.return_value = Mock(User, agentid=agent_id)
        mock_is_phone_exten.return_value = True
        mock_agent_context.return_value = agent_context
        self.agent_manager.login = Mock()

        self.agent_manager.on_cti_agent_login(self.connected_user_id, agent_id, self.agent_1_exten)

        self.agent_manager.login.assert_called_once_with(agent_id, self.agent_1_exten, agent_context)

    @patch('xivo_dao.user_line_dao.is_phone_exten')
    @patch('xivo_dao.agent_dao.agent_context')
    @patch('xivo_cti.tools.idconverter.IdConverter.xid_to_id')
    def test_on_cti_agent_login_when_extension_in_use(self,
                                                      mock_id_converter,
                                                      mock_agent_context,
                                                      mock_is_phone_exten):
        agent_id = 11
        agent_context = 'foobar'
        mock_id_converter.return_value = agent_id
        mock_agent_context.return_value = agent_context
        mock_is_phone_exten.return_value = True
        self.agent_executor.login.side_effect = ExtensionInUseError()

        result = self.agent_manager.on_cti_agent_login(self.connected_user_id, agent_id, self.agent_1_exten)

        self.assertEqual(result, ('error', {'error_string': 'agent_login_exten_in_use', 'class': 'ipbxcommand'}))
        self.agent_executor.login.assert_called_once_with(agent_id, self.agent_1_exten, agent_context)

    @patch('xivo_dao.user_line_dao.is_phone_exten')
    @patch('xivo_dao.agent_dao.agent_context')
    @patch('xivo_cti.tools.idconverter.IdConverter.xid_to_id')
    def test_on_cti_agent_login_when_no_such_extension(self,
                                                       mock_id_converter,
                                                       mock_agent_context,
                                                       mock_is_phone_exten):
        agent_id = 11
        agent_context = 'foobar'
        mock_id_converter.return_value = agent_id
        mock_agent_context.return_value = agent_context
        mock_is_phone_exten.return_value = True
        self.agent_executor.login.side_effect = NoSuchExtensionError()

        result = self.agent_manager.on_cti_agent_login(self.connected_user_id, agent_id, self.agent_1_exten)

        self.assertEqual(result, ('error', {'error_string': 'agent_login_invalid_exten', 'class': 'ipbxcommand'}))
        self.agent_executor.login.assert_called_once_with(agent_id, self.agent_1_exten, agent_context)

    @patch('xivo_dao.user_line_dao.is_phone_exten')
    @patch('xivo_dao.user_line_dao.get_main_exten_by_line_id')
    @patch('xivo_dao.user_line_dao.find_line_id_by_user_id')
    @patch('xivo_dao.agent_dao.agent_context')
    @patch('xivo_dao.resources.user.dao.find_all_by')
    @patch('xivo_dao.resources.user.dao.get')
    @patch('xivo_cti.tools.idconverter.IdConverter.xid_to_id')
    def test_on_cti_agent_login_no_number(self,
                                          mock_id_converter,
                                          mock_user_dao_get,
                                          mock_user_find_all_by,
                                          mock_agent_context,
                                          mock_find_line_id_by_user_id,
                                          mock_get_main_exten_by_line_id,
                                          mock_is_phone_exten):
        user_id = 10
        agent_id = 11
        line_id = 12
        agent_context = 'test_context'
        mock_id_converter.return_value = agent_id
        mock_user_dao_get.return_value = Mock(User, agentid=agent_id)
        mock_user_find_all_by.return_value = [Mock(User, agentid=user_id)]
        mock_find_line_id_by_user_id.return_value = [line_id]
        mock_get_main_exten_by_line_id.return_value = self.line_number
        mock_is_phone_exten.return_value = True
        mock_agent_context.return_value = agent_context
        self.agent_manager.login = Mock()

        self.agent_manager.on_cti_agent_login(self.connected_user_id, agent_id)

        self.agent_manager.login.assert_called_once_with(agent_id, self.line_number, agent_context)

    @patch('xivo_cti.tools.idconverter.IdConverter.xid_to_id')
    def test_on_cti_agent_logout(self, mock_id_converter):
        agent_id = 11
        mock_id_converter.return_value = agent_id
        self.agent_manager.logoff = Mock()

        self.agent_manager.on_cti_agent_logout(self.connected_user_id, agent_id)

        self.agent_manager.logoff.assert_called_once_with(agent_id)

    @patch('xivo_dao.resources.user.dao.find')
    @patch('xivo_dao.agent_status_dao.get_status')
    @patch('xivo_dao.user_line_dao.get_line_identity_by_user_id')
    def test_on_cti_listen(self, mock_get_line_identity, mock_get_status, mock_user_dao_find):
        agent_id = '42'
        connected_agent_id = '67'
        agent_xid = 'xivo/%s' % agent_id
        user_device = 'SIP/abcd'
        agent_device = 'SIP/fghi'
        connected_agent_device = 'SIP/zerg'
        agent_status = Mock()
        agent_status.state_interface = agent_device
        connected_agent_status = Mock()
        connected_agent_status.state_interface = connected_agent_device
        mock_get_line_identity.return_value = user_device
        mock_user_dao_find.return_value = Mock(User, agentid=connected_agent_id)

        mock_get_status.side_effect = lambda x: {agent_id: agent_status, connected_agent_id: connected_agent_status}[x]

        self.agent_manager.on_cti_listen(self.connected_user_id, agent_xid)

        mock_get_line_identity.assert_called_once_with(self.connected_user_id)
        mock_user_dao_find.assert_called_once_with(self.connected_user_id)
        mock_get_status.assert_any_call(agent_id)
        mock_get_status.assert_any_call(connected_agent_id)
        self.ami.sendcommand.assert_called_once_with('Originate',
                                                     [('Channel', connected_agent_device),
                                                      ('Application', 'ChanSpy'),
                                                      ('Data', '%s,bds' % agent_device),
                                                      ('CallerID', u'Listen/Écouter'),
                                                      ('Async', 'true')])

    @patch('xivo_dao.resources.user.dao.find')
    @patch('xivo_dao.agent_status_dao.get_status')
    @patch('xivo_dao.user_line_dao.get_line_identity_by_user_id')
    def test_on_cti_listen_supervisor_not_agent(self, mock_get_line_identity, mock_get_status, mock_user_dao_find):
        agent_id = '42'
        connected_agent_id = None
        agent_xid = 'xivo/%s' % agent_id
        user_device = 'SIP/abcd'
        agent_device = 'SIP/fghi'
        agent_status = Mock()
        agent_status.state_interface = agent_device
        mock_get_line_identity.return_value = user_device
        mock_user_dao_find.return_value = Mock(User, agentid=connected_agent_id)
        mock_get_status.return_value = agent_status

        self.agent_manager.on_cti_listen(self.connected_user_id, agent_xid)

        mock_get_line_identity.assert_called_once_with(self.connected_user_id)
        mock_user_dao_find.assert_called_once_with(self.connected_user_id)
        mock_get_status.assert_any_call(agent_id)
        self.ami.sendcommand.assert_called_once_with('Originate',
                                                     [('Channel', user_device),
                                                      ('Application', 'ChanSpy'),
                                                      ('Data', '%s,bds' % agent_device),
                                                      ('CallerID', u'Listen/Écouter'),
                                                      ('Async', 'true')])

    @patch('xivo_dao.agent_status_dao.get_status')
    @patch('xivo_dao.user_line_dao.get_line_identity_by_user_id')
    @patch('xivo_dao.resources.user.dao.find')
    def test_on_cti_listen_no_associated_line(self, mock_user_dao_find, mock_get_line_identity, mock_get_status):
        agent_id = '42'
        agent_xid = 'xivo/%s' % agent_id
        agent_device = 'SIP/fghi'
        agent_status = Mock()
        agent_status.state_interface = agent_device
        mock_get_line_identity.side_effect = LookupError
        mock_get_status.return_value = agent_status

        self.agent_manager.on_cti_listen(self.connected_user_id, agent_xid)

        mock_get_line_identity.assert_called_once_with(self.connected_user_id)
        mock_get_status.assert_any_call(agent_id)

        self.ami.sendcommand.assert_not_called()

    @patch('xivo_dao.resources.user.dao.find')
    @patch('xivo_dao.agent_status_dao.get_status')
    @patch('xivo_dao.user_line_dao.get_line_identity_by_user_id')
    def test_on_cti_listen_superviso_not_logged_on(self, mock_get_line_identity, mock_get_status, mock_user_dao_find):
        agent_id = '42'
        connected_agent_id = '67'
        agent_xid = 'xivo/%s' % agent_id
        user_device = 'SIP/abcd'
        agent_device = 'SIP/fghi'
        agent_status = Mock()
        agent_status.state_interface = agent_device
        mock_get_line_identity.return_value = user_device
        mock_user_dao_find.return_value = Mock(User, agentid=connected_agent_id)

        mock_get_status.side_effect = lambda x: {agent_id: agent_status, connected_agent_id: None}[x]

        self.agent_manager.on_cti_listen(self.connected_user_id, agent_xid)

        mock_get_line_identity.assert_called_once_with(self.connected_user_id)
        mock_user_dao_find.assert_called_once_with(self.connected_user_id)
        mock_get_status.assert_any_call(agent_id)
        mock_get_status.assert_any_call(connected_agent_id)
        self.ami.sendcommand.assert_called_once_with('Originate',
                                                     [('Channel', user_device),
                                                      ('Application', 'ChanSpy'),
                                                      ('Data', '%s,bds' % agent_device),
                                                      ('CallerID', u'Listen/Écouter'),
                                                      ('Async', 'true')])

    @patch('xivo_dao.user_line_dao.is_phone_exten')
    @patch('xivo_dao.user_line_dao.get_main_exten_by_line_id')
    @patch('xivo_dao.user_line_dao.find_line_id_by_user_id')
    @patch('xivo_dao.agent_dao.agent_context')
    @patch('xivo_dao.resources.user.dao.find_all_by')
    @patch('xivo_dao.resources.user.dao.find')
    @patch('xivo_cti.tools.idconverter.IdConverter.xid_to_id')
    def test_agent_special_me(self,
                              mock_id_converter,
                              mock_user_dao_find,
                              mock_user_dao_find_all_by,
                              mock_agent_context,
                              mock_find_line_id_by_user_id,
                              mock_get_main_exten_by_line_id,
                              mock_is_phone_exten):
        user_id = 12
        agent_id = 44
        agent_context = 'test_context'
        mock_id_converter.return_value = agent_id
        mock_user_dao_find.return_value = Mock(User, agentid=agent_id)
        mock_user_dao_find_all_by.return_value = [Mock(User, agentid=user_id)]
        mock_find_line_id_by_user_id.return_value = [13]
        mock_get_main_exten_by_line_id.return_value = self.line_number
        mock_is_phone_exten.return_value = True
        mock_agent_context.return_value = agent_context
        self.agent_manager.login = Mock()

        self.agent_manager.on_cti_agent_login(user_id, 'agent:special:me')

        self.agent_manager.login.assert_called_once_with(agent_id, self.line_number, agent_context)

    @patch('xivo_dao.user_line_dao.get_main_exten_by_line_id')
    @patch('xivo_dao.user_line_dao.find_line_id_by_user_id')
    @patch('xivo_dao.resources.user.dao.find_all_by')
    def test_find_agent_exten(self,
                              mock_user_find_all_by,
                              mock_find_line_id_by_user_id,
                              mock_get_main_exten_by_line_id):
        agent_id = 11
        mock_user_find_all_by.return_value = [Mock(User, agentid=12)]
        mock_find_line_id_by_user_id.return_value = [13]
        mock_get_main_exten_by_line_id.return_value = self.line_number

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

    def test_add_agent_to_queue(self):
        agent_id = 42
        queue_id = 1

        self.agent_manager.add_agent_to_queue(agent_id, queue_id)

        self.agent_executor.add_to_queue.assert_called_once_with(agent_id, queue_id)

    def test_remove_agent_from_queue(self):
        agent_id = 42
        queue_id = 1

        self.agent_manager.remove_agent_from_queue(agent_id, queue_id)

        self.agent_executor.remove_from_queue.assert_called_once_with(agent_id, queue_id)

    @patch('xivo_dao.queue_dao.queue_name')
    def test_pause_agent_on_queue(self, mock_queue_name):
        agent_id = 42
        agent_interface = 'SIP/abcdef'
        queue_id = 1
        queue_name = 'foobar'
        self.agent_manager._get_agent_interface = Mock()
        self.agent_manager._get_agent_interface.return_value = agent_interface
        mock_queue_name.return_value = queue_name

        self.agent_manager.pause_agent_on_queue(agent_id, queue_id)

        self.agent_executor.pause_on_queue.assert_called_once_with(agent_interface, queue_name)

    def test_pause_agent_on_all_queues(self):
        agent_id = 42
        agent_interface = 'SIP/abcdef'
        self.agent_manager._get_agent_interface = Mock()
        self.agent_manager._get_agent_interface.return_value = agent_interface

        self.agent_manager.pause_agent_on_all_queues(agent_id)

        self.agent_executor.pause_on_all_queues.assert_called_once_with(agent_interface)

    @patch('xivo_dao.queue_dao.queue_name')
    def test_unpause_agent_on_queue(self, mock_queue_name):
        agent_id = 42
        agent_interface = 'SIP/abcdef'
        queue_id = 1
        queue_name = 'foobar'
        self.agent_manager._get_agent_interface = Mock()
        self.agent_manager._get_agent_interface.return_value = agent_interface
        mock_queue_name.return_value = queue_name

        self.agent_manager.unpause_agent_on_queue(agent_id, queue_id)

        self.agent_executor.unpause_on_queue.assert_called_once_with(agent_interface, queue_name)

    def test_unpause_agent_on_all_queues(self):
        agent_id = 42
        agent_interface = 'SIP/abcdef'
        self.agent_manager._get_agent_interface = Mock()
        self.agent_manager._get_agent_interface.return_value = agent_interface

        self.agent_manager.unpause_agent_on_all_queues(agent_id)

        self.agent_executor.unpause_on_all_queues.assert_called_once_with(agent_interface)

    @patch('xivo_dao.agent_dao.find_agent_interface')
    def test_set_presence(self, mock_agent_interface):
        presence = 'disconnected'
        agent_id = 34
        agent_member_name = 'Agent/1234'
        mock_agent_interface.return_value = agent_member_name

        self.agent_manager.set_presence(agent_id, presence)

        self.agent_executor.log_presence.assert_called_once_with(agent_member_name, presence)
