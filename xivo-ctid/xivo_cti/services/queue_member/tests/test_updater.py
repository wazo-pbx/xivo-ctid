# -*- coding: UTF-8 -*-

import unittest
from mock import Mock, patch
from xivo_cti.services.queue_member.manager import QueueMemberManager
from xivo_cti.services.queue_member.updater import QueueMemberUpdater
from xivo_cti.xivo_ami import AMIClass
from xivo_cti.services.queue_member.common import format_queue_member_id


class TestQueueMemberUpdater(unittest.TestCase):

    def setUp(self):
        self.queue_member_manager = Mock(QueueMemberManager)
        self.ami_class = Mock(AMIClass)
        self.queue_member_updater = QueueMemberUpdater(self.queue_member_manager,
                                                       self.ami_class)

    @patch('xivo_dao.queue_member_dao.get_queue_members_for_queues')
    def test_add_dao_queue_members_on_update_request_queue_status_for_new_member(self, mock_get_queue_members):
        dao_queue_member = Mock()
        dao_queue_member.queue_name = 'queue1'
        dao_queue_member.member_name = 'member1'
        mock_get_queue_members.return_value = [dao_queue_member]
        self.queue_member_manager.get_queue_members_id.return_value = []

        self.queue_member_updater._add_dao_queue_members_on_update()

        self.ami_class.queuestatus.assert_called_once_with(dao_queue_member.queue_name,
                                                           dao_queue_member.member_name)

    @patch('xivo_dao.queue_member_dao.get_queue_members_for_queues')
    def test_add_dao_queue_members_on_update_does_not_request_queue_status_for_old_member(self, mock_get_queue_members):
        dao_queue_member = Mock()
        dao_queue_member.queue_name = 'queue1'
        dao_queue_member.member_name = 'member1'
        mock_get_queue_members.return_value = [dao_queue_member]
        queue_member_id = format_queue_member_id(dao_queue_member.queue_name,
                                                 dao_queue_member.member_name)
        self.queue_member_manager.get_queue_members_id.return_value = [queue_member_id]

        self.queue_member_updater._add_dao_queue_members_on_update()

        self.assertFalse(self.ami_class.called)

    @patch('xivo_cti.services.queue_member.member.QueueMember.from_ami_agent_added_to_queue')
    def test_on_ami_agent_added_to_queue(self, from_ami_agent_added_to_queue):
        ami_event = {'QueueName': 'queue1', 'AgentNumber': '123'}
        queue_member = Mock()
        from_ami_agent_added_to_queue.return_value = queue_member
        self.queue_member_updater._ask_member_queue_status = Mock()

        self.queue_member_updater.on_ami_agent_added_to_queue(ami_event)

        from_ami_agent_added_to_queue.assert_called_once_with('queue1', '123')
        self.queue_member_manager._add_queue_member.assert_called_once_with(queue_member)

    def test_on_ami_removed_from_queue(self):
        ami_event = {'QueueName': 'queue1', 'AgentNumber': '123'}

        self.queue_member_updater.on_ami_agent_removed_from_queue(ami_event)

        self.queue_member_manager._remove_queue_member_by_agent_number.assert_called_once_with('queue1', '123')
