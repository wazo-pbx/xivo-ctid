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
from xivo_cti.dao.userfeaturesdao import UserFeaturesDAO
from xivo_cti.services.agent_service_manager import AgentServiceManager
from xivo_cti.cti_config import Config


class TestPresenceServiceExecutor(unittest.TestCase):

    def setUp(self):
        self.user_service_manager = Mock(UserServiceManager)
        self.agent_service_manager = Mock(AgentServiceManager)
        self.user_features_dao = Mock(UserFeaturesDAO)
        self.config = Mock(Config)
        self.presence_service_executor = PresenceServiceExecutor(self.user_service_manager,
                                                                 self.agent_service_manager,
                                                                 self.user_features_dao,
                                                                 self.config)

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

    def test_execute_actions(self):
        user_id = 64
        user_profile = 'client'
        presence_group_name = 'xivo'

        self.presence_service_executor._launch_presence_service = Mock()

        self.presence_service_executor.user_features_dao.get_profile.return_value = user_profile
        self.presence_service_executor.config.getconfig.return_value = {
            'profiles': {user_profile: {'userstatus': presence_group_name}},
            'userstatus': {presence_group_name: self._get_userstatus()}
        }

        self.presence_service_executor.execute_actions(user_id, 'disconnected')

        self.presence_service_executor._launch_presence_service.assert_called_once_with(user_id, 'agentlogoff', False)

    def test_execute_actions_unknown(self):
        user_id = 64
        user_profile = 'client'
        presence_group_name = 'xivo'

        self.presence_service_executor.user_features_dao.get_profile.return_value = user_profile
        self.presence_service_executor.config.getconfig.return_value = {
            'profiles': {user_profile: {'userstatus': presence_group_name}},
            'userstatus': {presence_group_name: self._get_userstatus()}
        }

        fn = lambda: self.presence_service_executor.execute_actions(user_id, 'unknown')

        self.assertRaises(ValueError, fn)

    def test_launch_presence_service_dnd(self):
        user_id = 1234

        for param in [True, False]:
            self.presence_service_executor._launch_presence_service(user_id, 'enablednd', param)
            self.presence_service_executor.user_service_manager.set_dnd.assert_called_once_with(user_id, param)
            self.presence_service_executor.user_service_manager.reset_mock()

    def test_launch_presence_service_no_handler(self):
        un_handled = ['enablevoicemail',
                      'callrecord',
                      'incallfilter',
                      'enableunc',
                      'enablebusy',
                      'enablerna']

        for service in un_handled:
            fn = lambda: self.presence_service_executor._launch_presence_service('uid', service, True)
            self.assertRaises(NotImplementedError, fn)

    def test_launch_presence_service_unknown(self):
        fn = lambda: self.presence_service_executor._launch_presence_service('uid', 'unknown', True)
        self.assertRaises(NotImplementedError, fn)

    def test_launch_presence_queue_no_handler(self):
        un_handled = ['queueadd',
                      'queueremove',
                      'queuepause',
                      'queueunpause']

        for service in un_handled:
            fn = lambda: self.presence_service_executor._launch_presence_queue('uid', service)
            self.assertRaises(NotImplementedError, fn)

    def test_launch_presence_queue_unknown(self):
        fn = lambda: self.presence_service_executor._launch_presence_queue('uid', 'unknown')
        self.assertRaises(NotImplementedError, fn)
