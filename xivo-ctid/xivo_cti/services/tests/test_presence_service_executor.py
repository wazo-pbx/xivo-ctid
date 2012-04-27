# -*- coding: UTF-8 -*-

import unittest
from tests.mock import Mock
from xivo_cti.innerdata import Safe
from xivo_cti.services.presence_service_executor import PresenceServiceExecutor


class TestPresenceServiceExecutor(unittest.TestCase):
    def setUp(self):
        self.presence_service_executor = PresenceServiceExecutor()
        self.presence_service_executor._innerdata = Mock(Safe)

    def tearDown(self):
        pass

    def test_execute_actions(self):
        user_id = 64

        self.presence_service_executor.execute_actions(user_id, 'disconnect')

        self.presence_service_executor._innerdata.presence_action.assert_called_once_with(user_id)
