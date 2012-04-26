# -*- coding: UTF-8 -*-

import unittest
from tests.mock import Mock
from xivo_cti.innerdata import Safe
from xivo_cti.services.user_executor import UserExecutor


class TestUserExecutor(unittest.TestCase):
    def setUp(self):
        self.user_executor = UserExecutor()
        self.user_executor._innerdata = Mock(Safe)

    def tearDown(self):
        pass

    def test_notify_cti(self):
        user_id = 64

        self.user_executor.notify_cti(user_id)

        self.user_executor._innerdata.handle_cti_stack.assert_was_called_once_with('set', ('users', 'updatestatus', user_id))
        self.user_executor._innerdata.handle_cti_stack.assert_was_called_once_with('empty_stack')
