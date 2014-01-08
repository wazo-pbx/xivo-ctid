# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
