# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from mock import Mock
from mock import sentinel
from mock import patch

from hamcrest import assert_that
from hamcrest import equal_to

import xivo_cti.services.user.manager as user_service_manager
from xivo_cti.ioc.context import context
from xivo_cti.services.current_call.manager import CurrentCallManager
from xivo_cti.services.user.notifier import UserServiceNotifier
from xivo_cti.services.user.manager import UserServiceManager
from xivo_cti.services.funckey.manager import FunckeyManager
from xivo_cti.services.presence.executor import PresenceServiceExecutor
from xivo_cti.services.agent.manager import AgentServiceManager
from xivo_cti.services.presence.manager import PresenceServiceManager
from xivo_cti.services.device.manager import DeviceManager
from xivo_cti.dao.user_dao import UserDAO
from xivo_cti.xivo_ami import AMIClass
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.ami.ami_response_handler import AMIResponseHandler


class TestUserServiceManager(unittest.TestCase):

    def setUp(self):
        self.agent_service_manager = Mock(AgentServiceManager)
        self.presence_service_manager = Mock(PresenceServiceManager)
        self.presence_service_executor = Mock(PresenceServiceExecutor)
        self.device_manager = Mock(DeviceManager)
        self.funckey_manager = Mock(FunckeyManager)
        self.user_service_notifier = Mock(UserServiceNotifier)
        self.ami_class = Mock(AMIClass)
        self.user_service_manager = UserServiceManager(
            self.user_service_notifier,
            self.agent_service_manager,
            self.presence_service_manager,
            self.funckey_manager,
            self.device_manager,
            self.ami_class,
        )
        self.user_service_manager.presence_service_executor = self.presence_service_executor
        self.user_service_manager.dao.user = Mock(UserDAO)
        context.reset()

    def test_call_destination_url(self):
        user_id = sentinel
        number = '1234'
        url = 'exten:xivo/{0}'.format(number)
        action_id = 'abcdef'
        connection = Mock(CTI)
        self.user_service_manager._dial = Mock(return_value=action_id)
        self.user_service_manager._register_originate_response_callback = Mock()

        self.user_service_manager.call_destination(connection, user_id, url)

        self.user_service_manager._dial.assert_called_once_with(user_id, number)
        self.user_service_manager._register_originate_response_callback.assert_called_once_with(
            action_id, connection, user_id, number)

    def test_call_destination_exten(self):
        user_id = sentinel
        number = '1234'
        action_id = '34897345'
        connection = Mock(CTI)
        self.user_service_manager._dial = Mock(return_value=action_id)
        self.user_service_manager._register_originate_response_callback = Mock()

        self.user_service_manager.call_destination(connection, user_id, number)

        self.user_service_manager._dial.assert_called_once_with(user_id, number)

        self.user_service_manager._register_originate_response_callback.assert_called_once_with(
            action_id, connection, user_id, number)

    def test_register_originate_response_callback(self):
        action_id, user_id, exten = '8734534', '12', '324564'
        callback = Mock()
        self.user_service_manager._on_originate_response_callback = callback
        response = {'ActionID': action_id}
        connection = sentinel

        self.user_service_manager._register_originate_response_callback(action_id, connection, user_id, exten)

        AMIResponseHandler.get_instance().handle_response(response)
        callback.assert_called_once_with(connection, user_id, exten, response)

    def test_on_originate_response_callback_success(self):
        user_id = 1
        exten = '543'
        connection = Mock(CTI)
        connection.answer_cb = sentinel
        response = {
            'Response': 'Success',
            'ActionID': '123423847',
            'Message': 'Originate successfully queued',
        }
        self.user_service_manager._on_originate_success = Mock()

        self.user_service_manager._on_originate_response_callback(
            connection, user_id, exten, response,
        )

        self.user_service_manager._on_originate_success.assert_called_once_with(connection.answer_cb)

    def test_on_originate_response_callback_error(self):
        user_id = 1
        exten = '543'
        msg = 'Extension does not exist.'
        connection = Mock(CTI)
        response = {
            'Response': 'Error',
            'ActionID': '123456',
            'Message': msg,
        }
        self.user_service_manager._on_originate_error = Mock()

        self.user_service_manager._on_originate_response_callback(connection, user_id, exten, response)

        self.user_service_manager._on_originate_error.assert_called_once_with(connection, user_id, exten, msg)

    def test_on_originate_success(self):
        context.register('current_call_manager', Mock, CurrentCallManager)
        mock_current_call_manager = context.get('current_call_manager')
        user_id = sentinel

        self.user_service_manager._on_originate_success(user_id)

        mock_current_call_manager.schedule_answer.assert_called_once_with(
            user_id, user_service_manager.ORIGINATE_AUTO_ANSWER_DELAY)

    def test_on_originate_error(self):
        user_id, exten = '42', '1234'
        msg = 'Extension does not exist.'
        formatted_error = 'unreachable_extension:%s' % exten
        formatted_msg = {
            'class': 'ipbxcommand',
            'error_string': formatted_error,
        }
        connection = Mock(CTI)
        self.user_service_notifier.report_error = Mock()

        self.user_service_manager._on_originate_error(connection, user_id, exten, msg)

        connection.send_message.assert_called_once_with(formatted_msg)

    def test_dial(self):
        user_id = 654
        exten = '1234'
        user_line_proto = 'SIP'
        user_line_name = 'abcdefd'
        user_line_number = '1001'
        user_fullname = 'Bob'
        user_line_context = 'default'
        action_id = '12345'
        self.ami_class.originate.return_value = action_id
        self.user_service_manager.dao.user.get_fullname.return_value = user_fullname
        self.user_service_manager.dao.user.get_line.return_value = {
            'protocol': user_line_proto,
            'name': user_line_name,
            'number': user_line_number,
            'context': user_line_context,
        }

        return_value = self.user_service_manager._dial(user_id, exten)

        self.ami_class.originate.assert_called_once_with(
            user_line_proto,
            user_line_name,
            user_line_number,
            user_fullname,
            exten,
            exten,
            user_line_context,
        )

        assert_that(return_value, equal_to(action_id), 'Returned action id')

    def test_dial_no_line_no_stack_trace(self):
        user_id = 654
        exten = '1234'
        self.user_service_manager.dao.user.get_line.side_effect = LookupError()

        self.user_service_manager._dial(user_id, exten)

    def test_enable_dnd(self):
        user_id = 123

        self.user_service_manager.enable_dnd(user_id)

        self.user_service_manager.dao.user.enable_dnd.assert_called_once_with(user_id)
        self.user_service_notifier.dnd_enabled.assert_called_once_with(user_id)
        self.funckey_manager.dnd_in_use.assert_called_once_with(user_id, True)

    def test_disable_dnd(self):
        user_id = 241

        self.user_service_manager.disable_dnd(user_id)

        self.user_service_manager.dao.user.disable_dnd.assert_called_once_with(user_id)
        self.user_service_notifier.dnd_disabled.assert_called_once_with(user_id)
        self.funckey_manager.dnd_in_use.assert_called_once_with(user_id, False)

    def test_set_dnd(self):
        old_enable, self.user_service_manager.enable_dnd = self.user_service_manager.enable_dnd, Mock()
        old_disable, self.user_service_manager.disable_dnd = self.user_service_manager.disable_dnd, Mock()

        user_id = 555

        self.user_service_manager.set_dnd(user_id, True)

        self.user_service_manager.enable_dnd.assert_called_once_with(user_id)

        self.user_service_manager.set_dnd(user_id, False)

        self.user_service_manager.disable_dnd.assert_called_once_with(user_id)

        self.user_service_manager.enable_dnd = old_enable
        self.user_service_manager.disable_dnd = old_disable

    def test_enable_filter(self):
        user_id = 789

        self.user_service_manager.enable_filter(user_id)

        self.user_service_manager.dao.user.enable_filter.assert_called_once_with(user_id)
        self.user_service_notifier.filter_enabled.assert_called_once_with(user_id)
        self.funckey_manager.call_filter_in_use.assert_called_once_with(user_id, True)

    def test_disable_filter(self):
        user_id = 834

        self.user_service_manager.disable_filter(user_id)

        self.user_service_manager.dao.user.disable_filter.assert_called_once_with(user_id)
        self.user_service_notifier.filter_disabled.assert_called_once_with(user_id)
        self.funckey_manager.call_filter_in_use.assert_called_once_with(user_id, False)

    @patch('xivo_dao.phonefunckey_dao.get_dest_unc')
    def test_enable_unconditional_fwd(self, mock_get_dest_unc):
        user_id = 543321
        destination = '234'
        mock_get_dest_unc.return_value = [destination]

        self.user_service_manager.enable_unconditional_fwd(user_id, destination)

        self.user_service_manager.dao.user.enable_unconditional_fwd.assert_called_once_with(user_id, destination)
        self.user_service_notifier.unconditional_fwd_enabled.assert_called_once_with(user_id, destination)

        expected_calls = sorted([
            ((user_id, '', True), {}),
            ((user_id, destination, True), {})
        ])
        calls = sorted(self.funckey_manager.unconditional_fwd_in_use.call_args_list)

        self.assertEquals(calls, expected_calls)

    @patch('xivo_dao.phonefunckey_dao.get_dest_unc')
    def test_disable_unconditional_fwd(self, mock_get_dest_unc):
        user_id = 543
        destination = '1234'
        fwd_key_dest = '102'
        mock_get_dest_unc.return_value = [fwd_key_dest]

        self.user_service_manager.disable_unconditional_fwd(user_id, destination)

        self.user_service_manager.dao.user.disable_unconditional_fwd.assert_called_once_with(user_id, destination)
        self.user_service_notifier.unconditional_fwd_disabled.assert_called_once_with(user_id, destination)
        self.funckey_manager.disable_all_unconditional_fwd.assert_called_once_with(user_id)

    @patch('xivo_dao.phonefunckey_dao.get_dest_rna')
    def test_enable_rna_fwd(self, mock_get_dest_rna):
        user_id = 2345
        destination = '3456'
        mock_get_dest_rna.return_value = [destination]

        self.user_service_manager.enable_rna_fwd(user_id, destination)

        self.user_service_manager.dao.user.enable_rna_fwd.assert_called_once_with(user_id, destination)
        self.user_service_notifier.rna_fwd_enabled.assert_called_once_with(user_id, destination)
        self.funckey_manager.disable_all_rna_fwd.assert_called_once_with(user_id)
        self.funckey_manager.rna_fwd_in_use.assert_called_once_with(user_id, destination, True)

    @patch('xivo_dao.phonefunckey_dao.get_dest_rna')
    def test_disable_rna_fwd(self, mock_get_dest_rna):
        user_id = 2345
        destination = '3456'
        fwd_key_dest = '987'
        mock_get_dest_rna.return_value = [fwd_key_dest]

        self.user_service_manager.disable_rna_fwd(user_id, destination)

        self.user_service_manager.dao.user.disable_rna_fwd.assert_called_once_with(user_id, destination)
        self.user_service_notifier.rna_fwd_disabled.assert_called_once_with(user_id, destination)
        self.funckey_manager.disable_all_rna_fwd.assert_called_once_with(user_id)

    @patch('xivo_dao.phonefunckey_dao.get_dest_busy')
    def test_enable_busy_fwd(self, mock_get_dest_busy):
        user_id = 2345
        destination = '3456'
        fwd_key_dest = '3456'
        mock_get_dest_busy.return_value = [fwd_key_dest]

        self.user_service_manager.enable_busy_fwd(user_id, destination)

        self.user_service_manager.dao.user.enable_busy_fwd.assert_called_once_with(user_id, destination)
        self.user_service_notifier.busy_fwd_enabled.assert_called_once_with(user_id, destination)
        self.funckey_manager.disable_all_busy_fwd.assert_called_once_with(user_id)
        self.funckey_manager.busy_fwd_in_use.assert_called_once_with(user_id, destination, True)

    @patch('xivo_dao.phonefunckey_dao.get_dest_busy')
    def test_disable_busy_fwd(self, mock_get_dest_busy):
        user_id = 2345
        destination = '3456'
        fwd_key_dest = '666'
        mock_get_dest_busy.return_value = [fwd_key_dest]

        self.user_service_manager.disable_busy_fwd(user_id, destination)

        self.user_service_manager.dao.user.disable_busy_fwd.assert_called_once_with(user_id, destination)
        self.user_service_notifier.busy_fwd_disabled.assert_called_once_with(user_id, destination)
        self.funckey_manager.disable_all_busy_fwd.assert_called_once_with(user_id)

    @patch('xivo_dao.phonefunckey_dao.get_dest_busy')
    def test_enable_busy_fwd_not_funckey(self, mock_get_dest_busy):
        user_id = 2345
        destination = '3456'
        fwd_key_dest = '666'
        mock_get_dest_busy.return_value = [fwd_key_dest]

        self.user_service_manager.enable_busy_fwd(user_id, destination)

        self.user_service_manager.dao.user.enable_busy_fwd.assert_called_once_with(user_id, destination)
        self.user_service_notifier.busy_fwd_enabled.assert_called_once_with(user_id, destination)

    def test_disconnect(self):
        user_id = 95
        self.user_service_manager.set_presence = Mock()

        self.user_service_manager.disconnect(user_id)

        self.user_service_manager.dao.user.disconnect.assert_called_once_with(user_id)
        self.user_service_manager.set_presence.assert_called_once_with(user_id, 'disconnected')

    def test_disconnect_no_action(self):
        user_id = 95
        self.user_service_manager.set_presence = Mock()

        self.user_service_manager.disconnect_no_action(user_id)

        self.user_service_manager.dao.user.disconnect.assert_called_once_with(user_id)
        self.user_service_manager.set_presence.assert_called_once_with(user_id, 'disconnected', action=False)

    @patch('xivo_dao.user_dao.is_agent')
    @patch('xivo_dao.user_dao.get_profile')
    def test_set_valid_presence_no_agent(self, mock_get_profile, mock_is_agent):
        user_id = 95
        presence = 'disconnected'
        expected_presence = 'disconnected'
        user_profile = 'client'
        mock_get_profile.return_value = user_profile
        mock_is_agent.return_value = False
        self.presence_service_manager.is_valid_presence.return_value = True

        self.user_service_manager.set_presence(user_id, presence)

        self.user_service_manager.presence_service_manager.is_valid_presence.assert_called_once_with(user_profile, expected_presence)
        self.user_service_manager.dao.user.set_presence.assert_called_once_with(user_id, expected_presence)
        self.user_service_manager.presence_service_executor.execute_actions.assert_called_once_with(user_id, expected_presence)
        self.user_service_notifier.presence_updated.assert_called_once_with(user_id, expected_presence)
        mock_is_agent.assert_called_once_with(user_id)
        self.user_service_manager.agent_service_manager.set_presence.assert_never_called()

    @patch('xivo_dao.user_dao.is_agent')
    @patch('xivo_dao.user_dao.get_profile')
    def test_set_valid_presence_no_agent_no_action(self, mock_get_profile, mock_is_agent):
        user_id = 95
        presence = 'disconnected'
        expected_presence = 'disconnected'
        user_profile = 'client'
        mock_get_profile.return_value = user_profile
        mock_is_agent.return_value = False
        self.presence_service_manager.is_valid_presence.return_value = True

        self.user_service_manager.set_presence(user_id, presence, action=False)

        self.user_service_manager.presence_service_manager.is_valid_presence.assert_called_once_with(user_profile, expected_presence)
        self.user_service_manager.dao.user.set_presence.assert_called_once_with(user_id, expected_presence)
        self.user_service_manager.presence_service_executor.execute_actions.assert_never_called()
        self.user_service_notifier.presence_updated.assert_called_once_with(user_id, expected_presence)
        mock_is_agent.assert_called_once_with(user_id)
        self.user_service_manager.agent_service_manager.set_presence.assert_never_called()

    @patch('xivo_dao.user_dao.agent_id')
    @patch('xivo_dao.user_dao.is_agent')
    @patch('xivo_dao.user_dao.get_profile')
    def test_set_valid_presence_with_agent(self, mock_get_profile, mock_is_agent, mock_agent_id):
        user_id = 95
        expected_agent_id = 10
        presence = 'disconnected'
        expected_presence = 'disconnected'
        user_profile = 'client'
        mock_get_profile.return_value = user_profile
        mock_is_agent.return_value = True
        mock_agent_id.return_value = expected_agent_id
        self.presence_service_manager.is_valid_presence.return_value = True

        self.user_service_manager.set_presence(user_id, presence)

        self.user_service_manager.presence_service_manager.is_valid_presence.assert_called_once_with(user_profile, expected_presence)
        self.user_service_manager.dao.user.set_presence.assert_called_once_with(user_id, expected_presence)
        self.user_service_manager.presence_service_executor.execute_actions.assert_called_once_with(user_id, expected_presence)
        self.user_service_notifier.presence_updated.assert_called_once_with(user_id, expected_presence)
        mock_is_agent.assert_called_once_with(user_id)
        self.user_service_manager.agent_service_manager.set_presence.assert_called_once_with(expected_agent_id, expected_presence)

    @patch('xivo_dao.user_dao.is_agent')
    @patch('xivo_dao.user_dao.get_profile')
    def test_set_not_valid_presence(self, mock_get_profile, mock_is_agent):
        user_id = 95
        presence = 'disconnected'
        expected_presence = 'disconnected'
        user_profile = 'client'
        mock_get_profile.return_value = user_profile
        self.presence_service_manager.is_valid_presence.return_value = False

        self.user_service_manager.set_presence(user_id, presence)

        self.user_service_manager.presence_service_manager.is_valid_presence.assert_called_once_with(user_profile, expected_presence)

        self.assertEquals(self.user_service_manager.dao.user.set_presence.call_count, 0)
        self.assertEquals(self.user_service_manager.presence_service_executor.call_count, 0)
        self.assertEquals(self.user_service_notifier.presence_updated.call_count, 0)
        self.assertEquals(mock_is_agent.call_count, 0)
        self.assertEquals(self.user_service_manager.agent_service_manager.set_presence.call_count, 0)

    def test_pickup_the_phone(self):
        client_connection = Mock(CTI)

        self.user_service_manager.pickup_the_phone(client_connection)

        client_connection.answer_cb.assert_called_once_with()

    @patch('xivo_dao.user_dao.enable_recording')
    def test_enable_recording(self, mock_enable_recording):
        target = 37

        self.user_service_manager.enable_recording(target)

        mock_enable_recording.assert_called_once_with(target)
        self.user_service_notifier.recording_enabled.assert_called_once_with(target)

    @patch('xivo_dao.user_dao.disable_recording')
    def test_disable_recording(self, mock_disable_recording):
        target = 35

        self.user_service_manager.disable_recording(target)

        mock_disable_recording.assert_called_once_with(target)
        self.user_service_notifier.recording_disabled.assert_called_once_with(target)
