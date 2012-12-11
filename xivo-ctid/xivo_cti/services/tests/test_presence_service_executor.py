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
from tests.mock import Mock
from xivo_cti.services.presence_service_executor import PresenceServiceExecutor
from xivo_cti.services.user_service_manager import UserServiceManager
from xivo_cti.services.agent_service_manager import AgentServiceManager
from xivo_cti.cti_config import Config
from mock import patch
from xivo_cti.innerdata import Safe


class TestPresenceServiceExecutor(unittest.TestCase):

    def setUp(self):
        self.user_service_manager = Mock(UserServiceManager)
        self.agent_service_manager = Mock(AgentServiceManager)
        self.config = Mock(Config)
        self.innerdata = Mock(Safe)
        self.presence_service_executor = PresenceServiceExecutor(self.user_service_manager,
                                                                 self.agent_service_manager,
                                                                 self.config,
                                                                 self.innerdata)

    def _get_userstatus(self):
        return {'available': {
                    'color': '#08FD20',
                    'allowed': [
                        'away',
                        'outtolunch',
                        'donotdisturb',
                        'disconnected'
                    ],
                    'actions': {
                        'enablednd': 'false',
                        'queueunpause_all': 'true'
                    },
                    'longname': 'Disponible'
                },
                'disconnected': {
                    'color': '#202020',
                    'allowed': [
                        'available'
                    ],
                    'actions': {
                        'agentlogoff': ''
                    },
                    'longname': u'D\xe9connect\xe9'
                }
            }

    @patch('xivo_dao.userfeatures_dao.agent_id')
    @patch('xivo_dao.userfeatures_dao.get_profile')
    def test_execute_actions_with_disconnected(self, mock_get_profile, mock_agent_id):
        user_id = 64
        agent_id = 33
        user_profile = 'client'
        presence_group_name = 'xivo'

        mock_agent_id.return_value = agent_id
        mock_get_profile.return_value = user_profile
        self.presence_service_executor.config.getconfig.return_value = {
            'profiles': {user_profile: {'userstatus': presence_group_name}},
            'userstatus': {presence_group_name: self._get_userstatus()}
        }

        self.presence_service_executor.execute_actions(user_id, 'disconnected')

        self.agent_service_manager.logoff.assert_called_once_with(agent_id)

    @patch('xivo_dao.userfeatures_dao.agent_id')
    @patch('xivo_dao.userfeatures_dao.get_profile')
    def test_execute_actions_with_available(self, mock_get_profile, mock_agent_id):
        user_id = 64
        agent_id = 33
        user_profile = 'client'
        presence_group_name = 'xivo'

        mock_agent_id.return_value = agent_id
        mock_get_profile.return_value = user_profile
        self.presence_service_executor.config.getconfig.return_value = {
            'profiles': {user_profile: {'userstatus': presence_group_name}},
            'userstatus': {presence_group_name: self._get_userstatus()}
        }

        self.presence_service_executor.execute_actions(user_id, 'available')

        self.user_service_manager.set_dnd.assert_called_once_with(user_id, False)
        self.agent_service_manager.queueunpause_all.assert_called_once_with(agent_id)

    @patch('xivo_dao.userfeatures_dao.get_profile')
    def test_execute_actions_unknown(self, mock_get_profile):
        user_id = 64
        user_profile = 'client'
        presence_group_name = 'xivo'

        mock_get_profile.return_value = user_profile
        self.presence_service_executor.config.getconfig.return_value = {
            'profiles': {user_profile: {'userstatus': presence_group_name}},
            'userstatus': {presence_group_name: self._get_userstatus()}
        }

        fn = lambda: self.presence_service_executor.execute_actions(user_id, 'unknown')

        self.assertRaises(ValueError, fn)
