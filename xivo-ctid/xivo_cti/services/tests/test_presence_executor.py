# -*- coding: UTF-8 -*-

import unittest
from tests.mock import Mock
from xivo_cti.innerdata import Safe
from xivo_cti.services.presence_executor import PresenceExecutor


class TestPresenceExecutor(unittest.TestCase):
    def setUp(self):
        self.presence_executor = PresenceExecutor()
        self.presence_executor._innerdata = Mock(Safe)

    def tearDown(self):
        pass

    def test_disconnect(self):
        user_id = 64

        self.presence_executor.disconnect(user_id)

        self.presence_executor._innerdata.presence_action.assert_called_once_with(user_id)
