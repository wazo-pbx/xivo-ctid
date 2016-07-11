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
import uuid

from concurrent import futures
from functools import wraps

from mock import ANY
from mock import Mock
from mock import sentinel as s
from mock import patch

from hamcrest import assert_that, calling, equal_to, not_, raises

from xivo_bus import Publisher

from xivo_cti.async_runner import AsyncRunner, synchronize
from xivo_cti.bus_listener import BusListener
from xivo_cti.task_queue import new_task_queue
from xivo_cti.dao.forward_dao import ForwardDAO
from xivo_cti.dao.user_dao import UserDAO
from xivo_cti.exception import NoSuchUserException
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.ioc.context import context
from xivo_cti.services.agent.manager import AgentServiceManager
from xivo_cti.services.funckey.manager import FunckeyManager
from xivo_cti.services.presence.executor import PresenceServiceExecutor
from xivo_cti.services.presence.manager import PresenceServiceManager
from xivo_cti.services.user.manager import UserServiceManager
from xivo_cti.services.user.notifier import UserServiceNotifier

SOME_UUID = str(uuid.uuid4())
SOME_TOKEN = str(uuid.uuid4())
CONFIG = {'confd': {}}


def mocked_confd_client(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        with patch('xivo_cti.services.user.manager.ConfdClient') as ConfdClientKlass:
            mocked_client = ConfdClientKlass.return_value
            f(*args, client=mocked_client, **kwargs)
    return wrapped


class _BaseTestCase(unittest.TestCase):

    def setUp(self):
        self._task_queue = new_task_queue()
        self._runner = AsyncRunner(futures.ThreadPoolExecutor(max_workers=1), self._task_queue)

        self.agent_service_manager = Mock(AgentServiceManager)
        self.presence_service_manager = Mock(PresenceServiceManager)
        self.presence_service_executor = Mock(PresenceServiceExecutor)
        self.funckey_manager = Mock(FunckeyManager)
        self.forward_dao = Mock(ForwardDAO)
        self.user_service_notifier = Mock(UserServiceNotifier)
        self._bus_listener = Mock(BusListener)
        self._bus_publisher = Mock(Publisher)
        self.user_service_manager = UserServiceManager(
            self.user_service_notifier,
            self.agent_service_manager,
            self.presence_service_manager,
            self.funckey_manager,
            self._runner,
            self._bus_listener,
            self._bus_publisher,
            self._task_queue
        )
        self.user_service_manager.presence_service_executor = self.presence_service_executor
        self.user_dao = self.user_service_manager.dao.user = Mock(UserDAO)
        self.user_service_manager.dao.forward = self.forward_dao

        context.reset()


@patch('xivo_cti.services.user.manager.config', CONFIG)
class TestUserServiceManager(_BaseTestCase):

    def test_connect(self):
        with patch.object(self.user_service_manager, 'send_presence') as send_presence:
            self.user_service_manager.connect(s.user_id, SOME_UUID, SOME_TOKEN, s.state)

        send_presence.assert_called_once_with(SOME_UUID, s.state)
        self.user_service_manager.dao.user.connect.assert_called_once_with(s.user_id)

    @mocked_confd_client
    def test_enable_dnd(self, client):
        with synchronize(self._runner):
            self.user_service_manager.enable_dnd(SOME_UUID, SOME_TOKEN)

        client.users(SOME_UUID).update_service.assert_called_once_with(service_name='dnd',
                                                                       service={'enabled': True})

    @mocked_confd_client
    def test_disable_dnd(self, client):
        with synchronize(self._runner):
            self.user_service_manager.disable_dnd(SOME_UUID, SOME_TOKEN)

        client.users(SOME_UUID).update_service.assert_called_once_with(service_name='dnd',
                                                                       service={'enabled': False})

    def test_set_dnd(self):
        with patch.object(self.user_service_manager, 'enable_dnd') as enable_dnd:
            self.user_service_manager.set_dnd(SOME_UUID, SOME_TOKEN, True)
            enable_dnd.assert_called_once_with(SOME_UUID, SOME_TOKEN)

        with patch.object(self.user_service_manager, 'disable_dnd') as disable_dnd:
            self.user_service_manager.set_dnd(SOME_UUID, SOME_TOKEN, False)
            disable_dnd.assert_called_once_with(SOME_UUID, SOME_TOKEN)

    @mocked_confd_client
    def test_enable_incallfilter(self, client):
        with synchronize(self._runner):
            self.user_service_manager.enable_filter(SOME_UUID, SOME_TOKEN)

        client.users(SOME_UUID).update_service.assert_called_once_with(service_name='incallfilter',
                                                                       service={'enabled': True})

    @mocked_confd_client
    def test_disable_incallfilter(self, client):
        with synchronize(self._runner):
            self.user_service_manager.disable_filter(SOME_UUID, SOME_TOKEN)

        client.users(SOME_UUID).update_service.assert_called_once_with(service_name='incallfilter',
                                                                       service={'enabled': False})

    @mocked_confd_client
    def test_enable_busy_fwd(self, client):
        with synchronize(self._runner):
            self.user_service_manager.enable_busy_fwd(SOME_UUID, SOME_TOKEN, s.destination)

        client.users(SOME_UUID).update_forward.assert_called_once_with(forward_name='busy',
                                                                       forward={'enabled': True,
                                                                                'destination': s.destination})

    @mocked_confd_client
    def test_disable_busy_fwd(self, client):
        with synchronize(self._runner):
            self.user_service_manager.disable_busy_fwd(SOME_UUID, SOME_TOKEN, s.destination)

        client.users(SOME_UUID).update_forward.assert_called_once_with(forward_name='busy',
                                                                       forward={'enabled': False,
                                                                                'destination': s.destination})

    @mocked_confd_client
    def test_enable_rna_fwd(self, client):
        with synchronize(self._runner):
            self.user_service_manager.enable_rna_fwd(SOME_UUID, SOME_TOKEN, s.destination)

        client.users(SOME_UUID).update_forward.assert_called_once_with(forward_name='noanswer',
                                                                       forward={'enabled': True,
                                                                                'destination': s.destination})

    @mocked_confd_client
    def test_disable_rna_fwd(self, client):
        with synchronize(self._runner):
            self.user_service_manager.disable_rna_fwd(SOME_UUID, SOME_TOKEN, s.destination)

        client.users(SOME_UUID).update_forward.assert_called_once_with(forward_name='noanswer',
                                                                       forward={'enabled': False,
                                                                                'destination': s.destination})

    @mocked_confd_client
    def test_enable_unconditional_fwd(self, client):
        with synchronize(self._runner):
            self.user_service_manager.enable_unconditional_fwd(SOME_UUID, SOME_TOKEN, s.destination)

        client.users(SOME_UUID).update_forward.assert_called_once_with(forward_name='unconditional',
                                                                       forward={'enabled': True,
                                                                                'destination': s.destination})

    @mocked_confd_client
    def test_disable_unconditional_fwd(self, client):
        with synchronize(self._runner):
            self.user_service_manager.disable_unconditional_fwd(SOME_UUID, SOME_TOKEN, s.destination)

        client.users(SOME_UUID).update_forward.assert_called_once_with(forward_name='unconditional',
                                                                       forward={'enabled': False,
                                                                                'destination': s.destination})

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

        self.user_service_manager.deliver_busy_message(user_uuid, enabled, destination)

        self.user_service_manager.dao.user.set_busy_fwd.assert_called_once_with(user_id, enabled, destination)
        self.user_service_notifier.busy_fwd_enabled.assert_called_once_with(user_id, enabled, destination)
        self.funckey_manager.update_all_busy_fwd.assert_called_with(user_id, enabled, destination)

    def test_deliver_busy_message_not_funckey(self):
        user_id = '2345'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        destination = '3456'
        enabled = True
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}

        self.user_service_manager.deliver_busy_message(user_uuid, enabled, destination)

        self.user_service_manager.dao.user.set_busy_fwd.assert_called_once_with(user_id, enabled, destination)
        self.user_service_notifier.busy_fwd_enabled.assert_called_once_with(user_id, enabled, destination)
        self.funckey_manager.update_all_busy_fwd.assert_called_with(user_id, enabled, destination)

    def test_deliver_busy_message_true(self):
        user_id = '12'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        enabled = True
        destination = '123'
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}

        self.user_service_manager.deliver_busy_message(user_uuid, enabled, destination)

        self.user_service_manager.dao.user.set_busy_fwd.assert_called_once_with(user_id, enabled, destination)
        self.user_service_notifier.busy_fwd_enabled.assert_called_once_with(user_id, enabled, destination)
        self.funckey_manager.update_all_busy_fwd.assert_called_with(user_id, enabled, destination)

    def test_deliver_busy_message_no_user_found(self):
        self.user_service_manager.dao.user.get_by_uuid.side_effect = NoSuchUserException

        assert_that(calling(self.user_service_manager.deliver_busy_message)
                    .with_args('7f523550-03cf-4dac-a858-cb8afdb34775', False, ''),
                    not_(raises(NoSuchUserException)))
        assert_that(self.user_service_manager.dao.user.set_busy_fwd.called, equal_to(False))
        assert_that(self.user_service_notifier.busy_fwd_enabled.called, equal_to(False))
        assert_that(self.funckey_manager.update_all_busy_fwd.called, equal_to(False))

    def test_deliver_rna_message_false(self):
        user_id = '12'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        enabled = False
        destination = '123'
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}

        self.user_service_manager.deliver_rna_message(user_uuid, enabled, destination)

        self.user_service_manager.dao.user.set_rna_fwd.assert_called_once_with(user_id, enabled, destination)
        self.user_service_notifier.rna_fwd_enabled.assert_called_once_with(user_id, enabled, destination)
        self.funckey_manager.update_all_rna_fwd.assert_called_with(user_id, enabled, destination)

    def test_deliver_rna_message_true(self):
        user_id = '12'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        enabled = True
        destination = '123'
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}

        self.user_service_manager.deliver_rna_message(user_uuid, enabled, destination)

        self.user_service_manager.dao.user.set_rna_fwd.assert_called_once_with(user_id, enabled, destination)
        self.user_service_notifier.rna_fwd_enabled.assert_called_once_with(user_id, enabled, destination)
        self.funckey_manager.update_all_rna_fwd.assert_called_with(user_id, enabled, destination)

    def test_deliver_rna_message_no_user_found(self):
        self.user_service_manager.dao.user.get_by_uuid.side_effect = NoSuchUserException

        assert_that(calling(self.user_service_manager.deliver_rna_message)
                    .with_args('7f523550-03cf-4dac-a858-cb8afdb34775', False, ''),
                    not_(raises(NoSuchUserException)))
        assert_that(self.user_service_manager.dao.user.set_rna_fwd.called, equal_to(False))
        assert_that(self.user_service_notifier.rna_fwd_enabled.called, equal_to(False))
        assert_that(self.funckey_manager.update_all_rna_fwd.called, equal_to(False))

    def test_deliver_unconditional_message_false(self):
        user_id = '12'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        enabled = False
        destination = '123'
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}

        self.user_service_manager.deliver_unconditional_message(user_uuid, enabled, destination)

        self.user_service_manager.dao.user.set_unconditional_fwd.assert_called_once_with(user_id, enabled, destination)
        self.user_service_notifier.unconditional_fwd_enabled.assert_called_once_with(user_id, enabled, destination)
        self.funckey_manager.update_all_unconditional_fwd.assert_called_with(user_id, enabled, destination)

    def test_deliver_unconditional_message_true(self):
        user_id = '12'
        user_uuid = '7f523550-03cf-4dac-a858-cb8afdb34775'
        enabled = True
        destination = '123'
        self.user_service_manager.dao.user.get_by_uuid.return_value = {'id': user_id}

        self.user_service_manager.deliver_unconditional_message(user_uuid, enabled, destination)

        self.user_service_manager.dao.user.set_unconditional_fwd.assert_called_once_with(user_id, enabled, destination)
        self.user_service_notifier.unconditional_fwd_enabled.assert_called_once_with(user_id, enabled, destination)
        self.funckey_manager.update_all_unconditional_fwd.assert_called_with(user_id, enabled, destination)

    def test_deliver_unconditional_message_no_user_found(self):
        self.user_service_manager.dao.user.get_by_uuid.side_effect = NoSuchUserException

        assert_that(calling(self.user_service_manager.deliver_unconditional_message)
                    .with_args('7f523550-03cf-4dac-a858-cb8afdb34775', False, ''),
                    not_(raises(NoSuchUserException)))
        assert_that(self.user_service_manager.dao.user.set_unconditional_fwd.called, equal_to(False))
        assert_that(self.user_service_notifier.unconditional_fwd_enabled.called, equal_to(False))
        assert_that(self.funckey_manager.update_all_unconditional_fwd.called, equal_to(False))

    def test_disconnect(self):
        self.user_service_manager.set_presence = Mock()

        with patch.object(self.user_service_manager, 'send_presence') as send_presence:
            self.user_service_manager.disconnect(s.user_id, SOME_UUID)

        self.user_service_manager.dao.user.disconnect.assert_called_once_with(s.user_id)
        send_presence.assert_called_once_with(SOME_UUID, 'disconnected')

    def test_disconnect_no_action(self):
        self.user_service_manager.set_presence = Mock()

        self.user_service_manager.disconnect_no_action(s.user_id, SOME_UUID)

        self.user_service_manager.dao.user.disconnect.assert_called_once_with(s.user_id)
        self.user_service_manager.set_presence.assert_called_once_with(s.user_id,
                                                                       SOME_UUID,
                                                                       ANY,
                                                                       'disconnected',
                                                                       action=False)

    def test_set_valid_presence_no_agent(self):
        presence = 'disconnected'
        expected_presence = 'disconnected'
        user_profile = 42
        self.user_service_manager.dao.user.get_cti_profile_id.return_value = user_profile
        self.user_service_manager.dao.user.get_agent_id.return_value = None
        self.presence_service_manager.is_valid_presence.return_value = True

        self.user_service_manager.set_presence(s.user_id, SOME_UUID, SOME_TOKEN, presence)

        self.user_service_manager.presence_service_manager.is_valid_presence.assert_called_once_with(
            user_profile, expected_presence)
        self.user_service_manager.dao.user.set_presence.assert_called_once_with(s.user_id, expected_presence)
        self.user_service_manager.presence_service_executor.execute_actions.assert_called_once_with(
            s.user_id, SOME_UUID, SOME_TOKEN, expected_presence)
        self.user_service_notifier.presence_updated.assert_called_once_with(s.user_id, expected_presence)
        self.user_service_manager.dao.user.get_agent_id.assert_called_once_with(s.user_id)
        self.assertFalse(self.user_service_manager.agent_service_manager.set_presence.called)

    def test_set_valid_presence_no_agent_no_action(self):
        presence = 'disconnected'
        expected_presence = 'disconnected'
        user_profile = 42
        self.user_service_manager.dao.user.get_cti_profile_id.return_value = user_profile
        self.user_service_manager.dao.user.get_agent_id.return_value = None
        self.presence_service_manager.is_valid_presence.return_value = True

        self.user_service_manager.set_presence(s.user_id, SOME_UUID, SOME_TOKEN, presence, action=False)

        self.user_service_manager.presence_service_manager.is_valid_presence.assert_called_once_with(
            user_profile, expected_presence)
        self.user_service_manager.dao.user.set_presence.assert_called_once_with(s.user_id, expected_presence)
        self.assertFalse(self.user_service_manager.presence_service_executor.execute_actions.called)
        self.user_service_notifier.presence_updated.assert_called_once_with(s.user_id, expected_presence)
        self.user_service_manager.dao.user.get_agent_id.assert_called_once_with(s.user_id)
        self.assertFalse(self.user_service_manager.agent_service_manager.set_presence.called)

    def test_set_valid_presence_with_agent(self):
        expected_agent_id = 10
        presence = 'disconnected'
        expected_presence = 'disconnected'
        user_profile = 42
        self.user_service_manager.dao.user.get_cti_profile_id.return_value = user_profile
        self.user_service_manager.dao.user.get_agent_id.return_value = expected_agent_id
        self.presence_service_manager.is_valid_presence.return_value = True

        self.user_service_manager.set_presence(s.user_id, SOME_UUID, SOME_TOKEN, presence)

        self.user_service_manager.presence_service_manager.is_valid_presence.assert_called_once_with(
            user_profile, expected_presence)
        self.user_service_manager.dao.user.set_presence.assert_called_once_with(s.user_id, expected_presence)
        self.user_service_manager.presence_service_executor.execute_actions.assert_called_once_with(
            s.user_id, SOME_UUID, SOME_TOKEN, expected_presence)
        self.user_service_notifier.presence_updated.assert_called_once_with(s.user_id, expected_presence)
        self.user_service_manager.dao.user.get_agent_id.assert_called_once_with(s.user_id)
        self.user_service_manager.agent_service_manager.set_presence.assert_called_once_with(
            expected_agent_id, expected_presence)

    def test_set_not_valid_presence(self):
        presence = 'disconnected'
        expected_presence = 'disconnected'
        user_profile = 42
        self.user_service_manager.dao.user.get_cti_profile_id.return_value = user_profile
        self.presence_service_manager.is_valid_presence.return_value = False

        self.user_service_manager.set_presence(s.user_id, SOME_UUID, SOME_TOKEN, presence)

        self.user_service_manager.presence_service_manager.is_valid_presence.assert_called_once_with(
            user_profile, expected_presence)

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
        self.user_service_manager.enable_recording(s.target)

        mock_enable_service.assert_called_once_with(s.target, 'callrecord')
        self.user_service_notifier.recording_enabled.assert_called_once_with(s.target)

    @patch('xivo_cti.database.user_db.disable_service')
    def test_disable_recording(self, mock_disable_service):
        self.user_service_manager.disable_recording(s.target)

        mock_disable_service.assert_called_once_with(s.target, 'callrecord')
        self.user_service_notifier.recording_disabled.assert_called_once_with(s.target)
