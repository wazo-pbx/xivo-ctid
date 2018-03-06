# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock, patch
from xivo_cti.services.queue_member.indexer import QueueMemberIndexer


class TestQueueMemberIndexer(unittest.TestCase):

    def setUp(self):
        self.queue_member_cti_indexer = QueueMemberIndexer()

    @patch('xivo_cti.dao.queue')
    @patch('xivo_cti.dao.agent')
    def test_on_queue_member_added(self, mock_agent, mock_queue):
        queue_member = Mock()
        queue_member.member_name = 'somemember'
        queue_member.queue_name = 'somequeue'
        mock_queue.get_id_from_name.return_value = 42
        mock_agent.get_id_from_interface.return_value = 13

        self.queue_member_cti_indexer.on_queue_member_added(queue_member)

        mock_agent.add_to_queue.assert_called_once_with(13, 42)

    @patch('xivo_cti.dao.agent')
    def test_on_queue_member_added_not_agent(self, mock_agent):
        queue_member = Mock()
        queue_member.is_agent.return_value = False

        self.queue_member_cti_indexer.on_queue_member_added(queue_member)

        self.assertEquals(mock_agent.add_to_queue.call_count, 0)

    @patch('xivo_cti.dao.queue')
    @patch('xivo_cti.dao.agent')
    def test_on_queue_member_removed(self, mock_agent, mock_queue):
        queue_member = Mock()
        queue_member.member_name = 'somemember'
        queue_member.queue_name = 'somequeue'
        mock_queue.get_id_from_name.return_value = 42
        mock_agent.get_id_from_interface.return_value = 13

        self.queue_member_cti_indexer.on_queue_member_removed(queue_member)

        mock_agent.remove_from_queue.assert_called_once_with(13, 42)

    @patch('xivo_cti.dao.agent')
    def test_on_queue_member_removed_not_agent(self, mock_agent):
        queue_member = Mock()
        queue_member.is_agent.return_value = False

        self.queue_member_cti_indexer.on_queue_member_removed(queue_member)

        self.assertEquals(mock_agent.remove_from_queue.call_count, 0)
