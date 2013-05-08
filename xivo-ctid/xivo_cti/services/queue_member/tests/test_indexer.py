# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
from mock import Mock, patch
from xivo_cti.services.queue_member.indexer import QueueMemberIndexer


class TestQueueMemberIndexer(unittest.TestCase):

    def setUp(self):
        self.send_cti_event = Mock()
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
