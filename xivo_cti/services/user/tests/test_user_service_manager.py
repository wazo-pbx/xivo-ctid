# -*- coding: utf-8 -*-

# Copyright (C) 2007-2016 Avencall
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

from concurrent import futures
from mock import Mock
from mock import sentinel
from mock import patch

from hamcrest import assert_that, calling, equal_to, not_, raises

from xivo_confd_client import Client
from xivo_cti.async_runner import AsyncRunner, synchronize
from xivo_cti.bus_listener import BusListener
from xivo_cti.task_queue import new_task_queue
from xivo_cti.ami.ami_callback_handler import AMICallbackHandler
from xivo_cti.ami.ami_response_handler import AMIResponseHandler
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter
from xivo_cti.dao.forward_dao import ForwardDAO
from xivo_cti.dao.user_dao import UserDAO
from xivo_cti.exception import NoSuchUserException
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.ioc.context import context
from xivo_cti.services.agent.manager import AgentServiceManager
from xivo_cti.services.call.manager import CallManager
from xivo_cti.services.device.manager import DeviceManager
from xivo_cti.services.funckey.manager import FunckeyManager
from xivo_cti.services.presence.executor import PresenceServiceExecutor
from xivo_cti.services.presence.manager import PresenceServiceManager
from xivo_cti.services.user.manager import UserServiceManager
from xivo_cti.services.user.notifier import UserServiceNotifier
from xivo_cti.tools.extension import InvalidExtension
from xivo_cti.xivo_ami import AMIClass


class _BaseTestCase(unittest.TestCase):

    def setUp(self):
        self._task_queue = new_task_queue()
        self._runner = AsyncRunner(futures.ThreadPoolExecutor(max_workers=1), self._task_queue)
        self._client = Mock(Client).return_value

        self.agent_service_manager = Mock(AgentServiceManager)
        self.presence_service_manager = Mock(PresenceServiceManager)
        self.presence_service_executor = Mock(PresenceServiceExecutor)
        self.device_manager = Mock(DeviceManager)
        self.funckey_manager = Mock(FunckeyManager)
        self.forward_dao = Mock(ForwardDAO)
        self.user_service_notifier = Mock(UserServiceNotifier)
        self.ami_class = Mock(AMIClass)
        self._ami_cb_handler = Mock(AMICallbackHandler)
        self._call_manager = Mock(CallManager)
        self._bus_listener = Mock(BusListener)
        self.user_service_manager = UserServiceManager(
            self.user_service_notifier,
            self.agent_service_manager,
            self.presence_service_manager,
            self.funckey_manager,
            self.device_manager,
            self.ami_class,
            self._ami_cb_handler,
            self._call_manager,
            self._client,
            self._runner,
            self._bus_listener,
            self._task_queue
        )
        self.user_service_manager.presence_service_executor = self.presence_service_executor
        self.user_service_manager.dao.user = Mock(UserDAO)
        self.user_service_manager.dao.forward = self.forward_dao

        context.reset()


class TestUserServiceManager(_BaseTestCase):

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

    def test_call_destination_caller_id(self):
        user_id = sentinel.user_id
        number = '1234'
        caller_id = '"Alice Smith" <{}>'.format(number)
        action_id = sentinel.action_id
        connection = Mock(CTI)

        self.user_service_manager._dial = Mock(return_value=sentinel.action_id)
        self.user_service_manager._register_originate_response_callback = Mock()

        self.user_service_manager.call_destination(connection, user_id, caller_id)

        self.user_service_manager._dial.assert_called_once_with(user_id, number)
        self.user_service_manager._register_originate_response_callback.assert_called_once_with(
            action_id, connection, user_id, number
        )

    def test_call_destination_invalid_exten(self):
        user_id = sentinel.user_id
        exten = ''
        connection = Mock(CTI)

        self.user_service_manager._dial = Mock(side_effect=InvalidExtension(''))

        self.user_service_manager.call_destination(connection, user_id, exten)

        expected_message = CTIMessageFormatter.ipbxcommand_error('unreachable_extension:%s' % exten)
        connection.send_message.assert_called_once_with(expected_message)

    def test_connect(self):
        state = 'available'
        user_id = '42'

        with patch.object(self.user_service_manager, 'set_presence') as set_presence:
            self.user_service_manager.connect(user_id, state)

        set_presence.assert_called_once_with(user_id, state)
        self.user_service_manager.dao.user.connect.assert_called_once_with(user_id)

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
        connection = Mock(CTI)
        connection.answer_cb = sentinel
        response = {
            'Response': 'Success',
            'ActionID': '123423847',
            'Message': 'Originate successfully queued',
        }
        self.user_service_manager._on_originate_success = Mock()
        self.user_service_manager.dao.user.get_line = Mock(return_value=sentinel.line)

        self.user_service_manager._on_originate_response_callback(
            connection, sentinel.user_id, sentinel.exten, response,
        )

        self.user_service_manager._on_originate_success.assert_called_once_with(
            connection, sentinel.exten, sentinel.line)

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
        connection = Mock(CTI)
        line = {'protocol': 'SCCP', 'name': 'zzzz'}

        self.user_service_manager._on_originate_success(connection, sentinel.exten, line)

        self._call_manager.answer_next_ringing_call.assert_called_once_with(connection, 'SCCP/zzzz')
        expected_message = CTIMessageFormatter.dial_success(sentinel.exten)
        connection.send_message.assert_called_once_with(expected_message)

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

        with synchronize(self._runner):
            self.user_service_manager.enable_dnd(user_id)

        self._client.users(user_id).update_service.assert_called_once_with(service_name='dnd',
                                                                           service={'enabled': True})

    def test_disable_dnd(self):
        user_id = 123

        with synchronize(self._runner):
            self.user_service_manager.disable_dnd(user_id)

        self._client.users(user_id).update_service.assert_called_once_with(service_name='dnd',
                                                                           service={'enabled': False})

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

    def test_enable_incallfilter(self):
        user_id = 123

        with synchronize(self._runner):
            self.user_service_manager.enable_filter(user_id)

        self._client.users(user_id).update_service.assert_called_once_with(service_name='incallfilter',
                                                                           service={'enabled': True})

    def test_disable_incallfilter(self):
        user_id = 123

        with synchronize(self._runner):
            self.user_service_manager.disable_filter(user_id)

        self._client.users(user_id).update_service.assert_called_once_with(service_name='incallfilter',
                                                                           service={'enabled': False})

    def test_deliver_incallfilter_message_no_user_found(self):
        self.user_service_manager.dao.user.get_by_uuid.side_effect = NoSuchUserException

        assert_that(calling(self.user_service_manager.deliver_incallfilter_message)
                    .with_args('7f523550-03cf-4dac-a858-cb8afdb34775', False),
                    not_(raises(NoSuchUserException)))
        assert_that(self.user_service_manager.dao.user.set_incallfilter.called, equal_to(False))
        assert_that(self.user_service_notifier.incallfilter_enabled.called, equal_to(False))
        assert_that(self.funckey_manager.call_filter_in_use.called, equal_to(False))

    def test_deliver_dnd_message_no_user_found(self):
        self.user_service_manager.dao.user.get_by_uuid.side_effect = NoSuchUserException

        assert_that(calling(self.user_service_manager.deliver_dnd_message)
                    .with_args('7f523550-03cf-4dac-a858-cb8afdb34775', False),
                    not_(raises(NoSuchUserException)))
        assert_that(self.user_service_manager.dao.user.set_dnd.called, equal_to(False))
        assert_that(self.user_service_notifier.dnd_enabled.called, equal_to(False))
        assert_that(self.funckey_manager.dnd_in_use.called, equal_to(False))

    def test_deliver_incallfilter_message_false(self):
        user_id = '12'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}

        self.user_service_manager.deliver_incallfilter_message(user_uuid, False)

        self.user_service_manager.dao.user.set_incallfilter.assert_called_once_with(user_id, False)
        self.user_service_notifier.incallfilter_enabled.assert_called_once_with(user_id, False)
        self.funckey_manager.call_filter_in_use.assert_called_once_with(user_id, False)

    def test_deliver_incallfilter_message_true(self):
        user_id = '12'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}

        self.user_service_manager.deliver_incallfilter_message(user_uuid, True)

        self.user_service_manager.dao.user.set_incallfilter.assert_called_once_with(user_id, True)
        self.user_service_notifier.incallfilter_enabled.assert_called_once_with(user_id, True)
        self.funckey_manager.call_filter_in_use.assert_called_once_with(user_id, True)

    def test_deliver_dnd_message_false(self):
        user_id = '12'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}

        self.user_service_manager.deliver_dnd_message(user_uuid, False)

        self.user_service_manager.dao.user.set_dnd.assert_called_once_with(user_id, False)
        self.user_service_notifier.dnd_enabled.assert_called_once_with(user_id, False)
        self.funckey_manager.dnd_in_use.assert_called_once_with(user_id, False)

    def test_deliver_dnd_message_true(self):
        user_id = '12'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}

        self.user_service_manager.deliver_dnd_message(user_uuid, True)

        self.user_service_manager.dao.user.set_dnd.assert_called_once_with(user_id, True)
        self.user_service_notifier.dnd_enabled.assert_called_once_with(user_id, True)
        self.funckey_manager.dnd_in_use.assert_called_once_with(user_id, True)

    def test_deliver_busy_message_false(self):
        user_id = '12'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        enabled = False
        destination = '123'
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}
        self.forward_dao.busy_destinations.return_value = [destination]

        self.user_service_manager.deliver_busy_message(user_uuid, enabled, destination)

        self.user_service_manager.dao.user.set_busy_fwd.assert_called_once_with(user_id, enabled, destination)
        self.user_service_notifier.busy_fwd_enabled.assert_called_once_with(user_id, enabled, destination)
        self.funckey_manager.disable_all_busy_fwd.assert_called_once_with(user_id)

    def test_deliver_busy_message_not_funckey(self):
        user_id = '2345'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        destination = '3456'
        fwd_key_dest = '666'
        enabled = True
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}
        self.forward_dao.busy_destinations.return_value = [fwd_key_dest]

        self.user_service_manager.deliver_busy_message(user_uuid, enabled, destination)

        self.user_service_manager.dao.user.set_busy_fwd.assert_called_once_with(user_id, enabled, destination)
        self.user_service_notifier.busy_fwd_enabled.assert_called_once_with(user_id, enabled, destination)
        self.forward_dao.busy_destinations.assert_called_once_with(user_id)

    def test_deliver_busy_message_true(self):
        user_id = '12'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        enabled = True
        destination = '123'
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}
        self.forward_dao.busy_destinations.return_value = [destination]

        self.user_service_manager.deliver_busy_message(user_uuid, enabled, destination)

        self.user_service_manager.dao.user.set_busy_fwd.assert_called_once_with(user_id, enabled, destination)
        self.user_service_notifier.busy_fwd_enabled.assert_called_once_with(user_id, enabled, destination)
        self.funckey_manager.busy_fwd_in_use.assert_called_with(user_id, destination, enabled)
        self.funckey_manager.disable_all_busy_fwd.assert_called_once_with(user_id)
        self.forward_dao.busy_destinations.assert_called_once_with(user_id)

    def test_deliver_busy_message_no_user_found(self):
        self.user_service_manager.dao.user.get_by_uuid.side_effect = NoSuchUserException

        assert_that(calling(self.user_service_manager.deliver_busy_message)
                    .with_args('7f523550-03cf-4dac-a858-cb8afdb34775', False, ''),
                    not_(raises(NoSuchUserException)))
        assert_that(self.user_service_manager.dao.user.set_busy_fwd.called, equal_to(False))
        assert_that(self.user_service_notifier.busy_fwd_enabled.called, equal_to(False))

    def test_deliver_rna_message_false(self):
        user_id = '12'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        enabled = False
        destination = '123'
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}
        self.forward_dao.rna_destinations.return_value = [destination]

        self.user_service_manager.deliver_rna_message(user_uuid, enabled, destination)

        self.user_service_manager.dao.user.set_rna_fwd.assert_called_once_with(user_id, enabled, destination)
        self.user_service_notifier.rna_fwd_enabled.assert_called_once_with(user_id, enabled, destination)
        self.funckey_manager.disable_all_rna_fwd.assert_called_once_with(user_id)

    def test_deliver_rna_message_true(self):
        user_id = '12'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        enabled = True
        destination = '123'
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}
        self.forward_dao.rna_destinations.return_value = [destination]

        self.user_service_manager.deliver_rna_message(user_uuid, enabled, destination)

        self.user_service_manager.dao.user.set_rna_fwd.assert_called_once_with(user_id, enabled, destination)
        self.user_service_notifier.rna_fwd_enabled.assert_called_once_with(user_id, enabled, destination)
        self.funckey_manager.rna_fwd_in_use.assert_called_with(user_id, destination, enabled)
        self.forward_dao.rna_destinations.assert_called_once_with(user_id)

    def test_deliver_rna_message_no_user_found(self):
        self.user_service_manager.dao.user.get_by_uuid.side_effect = NoSuchUserException

        assert_that(calling(self.user_service_manager.deliver_rna_message)
                    .with_args('7f523550-03cf-4dac-a858-cb8afdb34775', False, ''),
                    not_(raises(NoSuchUserException)))
        assert_that(self.user_service_manager.dao.user.set_rna_fwd.called, equal_to(False))
        assert_that(self.user_service_notifier.rna_fwd_enabled.called, equal_to(False))

    def test_deliver_unconditional_message_false(self):
        user_id = '12'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        enabled = False
        destination = '123'
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}

        self.user_service_manager.deliver_unconditional_message(user_uuid, enabled, destination)

        self.user_service_manager.dao.user.set_unconditional_fwd.assert_called_once_with(user_id, enabled, destination)
        self.user_service_notifier.unconditional_fwd_enabled.assert_called_once_with(user_id, enabled, destination)
        self.funckey_manager.disable_all_unconditional_fwd.assert_called_once_with(user_id)

    def test_deliver_unconditional_message_true(self):
        user_id = '12'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        enabled = True
        destination = '123'
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}
        self.forward_dao.unc_destinations.return_value = [destination]

        self.user_service_manager.deliver_unconditional_message(user_uuid, enabled, destination)

        self.user_service_manager.dao.user.set_unconditional_fwd.assert_called_once_with(user_id, enabled, destination)
        self.user_service_notifier.unconditional_fwd_enabled.assert_called_once_with(user_id, enabled, destination)
        self.forward_dao.unc_destinations.assert_called_once_with(user_id)

        expected_calls = sorted([((user_id, '', True), {}),
                                 ((user_id, destination, True), {})])
        calls = sorted(self.funckey_manager.unconditional_fwd_in_use.call_args_list)
        self.assertEquals(calls, expected_calls)

    def test_deliver_unconditional_message_no_user_found(self):
        self.user_service_manager.dao.user.get_by_uuid.side_effect = NoSuchUserException

        assert_that(calling(self.user_service_manager.deliver_unconditional_message)
                    .with_args('7f523550-03cf-4dac-a858-cb8afdb34775', False, ''),
                    not_(raises(NoSuchUserException)))
        assert_that(self.user_service_manager.dao.user.set_unconditional_fwd.called, equal_to(False))
        assert_that(self.user_service_notifier.unconditional_fwd_enabled.called, equal_to(False))

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

    def test_set_valid_presence_no_agent(self):
        user_id = '95'
        presence = 'disconnected'
        expected_presence = 'disconnected'
        user_profile = 42
        self.user_service_manager.dao.user.get_cti_profile_id.return_value = user_profile
        self.user_service_manager.dao.user.get_agent_id.return_value = None
        self.presence_service_manager.is_valid_presence.return_value = True

        self.user_service_manager.set_presence(user_id, presence)

        self.user_service_manager.presence_service_manager.is_valid_presence.assert_called_once_with(user_profile, expected_presence)
        self.user_service_manager.dao.user.set_presence.assert_called_once_with(user_id, expected_presence)
        self.user_service_manager.presence_service_executor.execute_actions.assert_called_once_with(user_id, expected_presence)
        self.user_service_notifier.presence_updated.assert_called_once_with(user_id, expected_presence)
        self.user_service_manager.dao.user.get_agent_id.assert_called_once_with(user_id)
        self.assertFalse(self.user_service_manager.agent_service_manager.set_presence.called)

    def test_set_valid_presence_no_agent_no_action(self):
        user_id = '95'
        presence = 'disconnected'
        expected_presence = 'disconnected'
        user_profile = 42
        self.user_service_manager.dao.user.get_cti_profile_id.return_value = user_profile
        self.user_service_manager.dao.user.get_agent_id.return_value = None
        self.presence_service_manager.is_valid_presence.return_value = True

        self.user_service_manager.set_presence(user_id, presence, action=False)

        self.user_service_manager.presence_service_manager.is_valid_presence.assert_called_once_with(user_profile, expected_presence)
        self.user_service_manager.dao.user.set_presence.assert_called_once_with(user_id, expected_presence)
        self.assertFalse(self.user_service_manager.presence_service_executor.execute_actions.called)
        self.user_service_notifier.presence_updated.assert_called_once_with(user_id, expected_presence)
        self.user_service_manager.dao.user.get_agent_id.assert_called_once_with(user_id)
        self.assertFalse(self.user_service_manager.agent_service_manager.set_presence.called)

    def test_set_valid_presence_with_agent(self):
        user_id = '95'
        expected_agent_id = 10
        presence = 'disconnected'
        expected_presence = 'disconnected'
        user_profile = 42
        self.user_service_manager.dao.user.get_cti_profile_id.return_value = user_profile
        self.user_service_manager.dao.user.get_agent_id.return_value = expected_agent_id
        self.presence_service_manager.is_valid_presence.return_value = True

        self.user_service_manager.set_presence(user_id, presence)

        self.user_service_manager.presence_service_manager.is_valid_presence.assert_called_once_with(user_profile, expected_presence)
        self.user_service_manager.dao.user.set_presence.assert_called_once_with(user_id, expected_presence)
        self.user_service_manager.presence_service_executor.execute_actions.assert_called_once_with(user_id, expected_presence)
        self.user_service_notifier.presence_updated.assert_called_once_with(user_id, expected_presence)
        self.user_service_manager.dao.user.get_agent_id.assert_called_once_with(user_id)
        self.user_service_manager.agent_service_manager.set_presence.assert_called_once_with(expected_agent_id, expected_presence)

    def test_set_not_valid_presence(self):
        user_id = '95'
        presence = 'disconnected'
        expected_presence = 'disconnected'
        user_profile = 42
        self.user_service_manager.dao.user.get_cti_profile_id.return_value = user_profile
        self.presence_service_manager.is_valid_presence.return_value = False

        self.user_service_manager.set_presence(user_id, presence)

        self.user_service_manager.presence_service_manager.is_valid_presence.assert_called_once_with(user_profile, expected_presence)

        self.assertEquals(self.user_service_manager.dao.user.set_presence.call_count, 0)
        self.assertEquals(self.user_service_manager.presence_service_executor.call_count, 0)
        self.assertEquals(self.user_service_notifier.presence_updated.call_count, 0)
        self.assertEquals(self.user_service_manager.dao.user.get_agent_id.call_count, 0)
        self.assertEquals(self.user_service_manager.agent_service_manager.set_presence.call_count, 0)

    def test_pickup_the_phone(self):
        client_connection = Mock(CTI)

        self.user_service_manager.pickup_the_phone(client_connection)

        client_connection.answer_cb.assert_called_once_with()

    @patch('xivo_cti.database.user_db.enable_service')
    def test_enable_recording(self, mock_enable_service):
        target = 37

        self.user_service_manager.enable_recording(target)

        mock_enable_service.assert_called_once_with(target, 'callrecord')
        self.user_service_notifier.recording_enabled.assert_called_once_with(target)

    @patch('xivo_cti.database.user_db.disable_service')
    def test_disable_recording(self, mock_disable_service):
        target = 35

        self.user_service_manager.disable_recording(target)

        mock_disable_service.assert_called_once_with(target, 'callrecord')
        self.user_service_notifier.recording_disabled.assert_called_once_with(target)
