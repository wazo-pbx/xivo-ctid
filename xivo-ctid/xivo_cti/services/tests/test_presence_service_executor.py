# -*- coding: UTF-8 -*-

import unittest
from tests.mock import Mock
from xivo_cti.services.presence_service_executor import PresenceServiceExecutor
from xivo_cti.services.user_service_manager import UserServiceManager
from xivo_cti.innerdata import Safe
from xivo_cti.dao.userfeaturesdao import UserFeaturesDAO
from xivo_cti.services.agent_service_manager import AgentServiceManager


class TestPresenceServiceExecutor(unittest.TestCase):
    def setUp(self):
        self.presence_service_executor = PresenceServiceExecutor()
        self.presence_service_executor._innerdata = Mock(Safe)
        self.presence_service_executor.user_service_manager = Mock(UserServiceManager)
        self.presence_service_executor.agent_service_manager = Mock(AgentServiceManager)
        self.presence_service_executor.user_features_dao = Mock(UserFeaturesDAO)

    def tearDown(self):
        pass

    def _get_user_permissions(self):
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

        self.presence_service_executor._innerdata.get_user_permissions.return_value = self._get_user_permissions()

        self.presence_service_executor.execute_actions(user_id, 'disconnected')

        self.presence_service_executor._innerdata.get_user_permissions.assert_called_once_with('userstatus', user_id)

    def test_execute_actions_unknown(self):
        user_id = 64

        self.presence_service_executor._innerdata.get_user_permissions.return_value = self._get_user_permissions()

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
