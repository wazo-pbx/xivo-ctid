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

from hamcrest import assert_that, calling, raises
from mock import Mock, patch

from xivo_cti.dao.user_dao import UserDAO

from xivo_cti.services.presence.executor import PresenceServiceExecutor
from xivo_cti.services.user.manager import UserServiceManager
from xivo_cti.services.agent.manager import AgentServiceManager


SOME_UUID = str(uuid.uuid4())
SOME_TOKEN = str(uuid.uuid4())


class TestPresenceServiceExecutor(unittest.TestCase):

    def setUp(self):
        self.user_service_manager = Mock(UserServiceManager)
        self.agent_service_manager = Mock(AgentServiceManager)
        self.presence_service_executor = PresenceServiceExecutor(self.user_service_manager,
                                                                 self.agent_service_manager)

    def _get_userstatus(self):
        return {
            'available': {
                'color': '#08FD20',
                'allowed': [
                    'away',
                    'outtolunch',
                    'donotdisturb',
                    'disconnected'
                ],
                'actions': {'enablednd': 'false',
                            'queueunpause_all': 'true'},
                'longname': 'Disponible'
            },
            'disconnected': {
                'color': '#202020',
                'allowed': [
                    'available'
                ],
                'actions': {'agentlogoff': ''},
                'longname': u'D\xe9connect\xe9'
            }
        }

    @patch('xivo_cti.dao.user', spec=UserDAO)
    def test_execute_actions_with_disconnected(self, mock_user_dao):
        user_id = '64'
        agent_id = 33
        user_profile = 2

        mock_user_dao.get_agent_id.return_value = agent_id
        mock_user_dao.get_cti_profile_id.return_value = user_profile

        with patch('xivo_cti.services.presence.executor.config',
                   {'profiles': {user_profile: {'userstatus': 'xivo'}},
                    'userstatus': {'xivo': self._get_userstatus()}}):
            self.presence_service_executor.execute_actions(user_id, SOME_UUID, SOME_TOKEN, 'disconnected')

        self.agent_service_manager.logoff.assert_called_once_with(agent_id)

    @patch('xivo_cti.dao.user', spec=UserDAO)
    def test_execute_actions_with_available(self, mock_user_dao):
        user_id = '64'
        agent_id = 33
        user_profile = 2

        mock_user_dao.get_agent_id.return_value = agent_id
        mock_user_dao.get_cti_profile_id.return_value = user_profile

        with patch('xivo_cti.services.presence.executor.config',
                   {'profiles': {user_profile: {'userstatus': 'xivo'}},
                    'userstatus': {'xivo': self._get_userstatus()}}):
            self.presence_service_executor.execute_actions(user_id, SOME_UUID, SOME_TOKEN, 'available')

        self.user_service_manager.set_dnd.assert_called_once_with(SOME_UUID, SOME_TOKEN, False)
        self.agent_service_manager.unpause_agent_on_all_queues.assert_called_once_with(agent_id)

    @patch('xivo_cti.dao.user', spec=UserDAO)
    def test_execute_actions_unknown(self, mock_user_dao):
        user_id = '64'
        user_profile = 2

        mock_user_dao.get_cti_profile_id.return_value = user_profile

        with patch('xivo_cti.services.presence.executor.config',
                   {'profiles': {user_profile: {'userstatus': 'xivo'}},
                    'userstatus': {'xivo': self._get_userstatus()}}):

            assert_that(calling(self.presence_service_executor.execute_actions)
                        .with_args(user_id, SOME_UUID, SOME_TOKEN, 'unknown'),
                        raises(ValueError))
