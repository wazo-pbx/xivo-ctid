# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock
from xivo_cti.services.queue_member.manager import QueueMemberManager
from xivo_cti.services.queue_member.cti.adapter import QueueMemberCTIAdapter


class TestQueueMemberCTIAdapter(unittest.TestCase):

    def setUp(self):
        self.queue_member_manager = Mock(QueueMemberManager)
        self.queue_member_cti_adapter = QueueMemberCTIAdapter(self.queue_member_manager)

    def test_get_list(self):
        self.queue_member_manager.get_queue_members_id.return_value = ['id1', 'id2']

        result = self.queue_member_cti_adapter.get_list()

        self.assertEqual(result, ['id1', 'id2'])
        self.queue_member_manager.get_queue_members_id.assert_called_once_with()

    def test_get_config_when_exist(self):
        queue_member = Mock()
        queue_member.to_cti_config.return_value = {'a': 'b'}
        self.queue_member_manager.get_queue_member.return_value = queue_member

        result = self.queue_member_cti_adapter.get_config('someid')

        self.queue_member_manager.get_queue_member.assert_called_once_with('someid')
        queue_member.to_cti_config.assert_called_once_with()
        self.assertEqual(result, {'a': 'b'})

    def test_get_config_when_not_exist(self):
        self.queue_member_manager.get_queue_member.return_value = None

        result = self.queue_member_cti_adapter.get_config('someid')

        self.queue_member_manager.get_queue_member.assert_called_once_with('someid')
        self.assertEqual(result, {})

    def test_get_status_when_exist(self):
        queue_member = Mock()
        queue_member.to_cti_status.return_value = {'a': 'b'}
        self.queue_member_manager.get_queue_member.return_value = queue_member

        result = self.queue_member_cti_adapter.get_status('someid')

        self.queue_member_manager.get_queue_member.assert_called_once_with('someid')
        queue_member.to_cti_status.assert_called_once_with()
        self.assertEqual(result, {'a': 'b'})

    def test_get_status_when_not_exist(self):
        self.queue_member_manager.get_queue_member.return_value = None

        result = self.queue_member_cti_adapter.get_status('someid')

        self.queue_member_manager.get_queue_member.assert_called_once_with('someid')
        self.assertEqual(result, None)
