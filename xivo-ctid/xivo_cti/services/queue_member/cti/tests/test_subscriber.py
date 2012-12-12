# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter
from xivo_cti.services.queue_member.cti.subscriber import QueueMemberCTISubscriber


class TestQueueMemberCTISubscriber(unittest.TestCase):

    def setUp(self):
        self.cti_message_formatter = Mock(CTIMessageFormatter)
        self.send_cti_event = Mock()
        self.queue_member_cti_subscriber = QueueMemberCTISubscriber(self.cti_message_formatter)
        self.queue_member_cti_subscriber.send_cti_event = self.send_cti_event

    def test_on_queue_member_added(self):
        queue_member = Mock()
        queue_member.id = 'someid'
        self.cti_message_formatter.add_queue_members.return_value = 'add_msg'

        self.queue_member_cti_subscriber.on_queue_member_added(queue_member)

        self.cti_message_formatter.add_queue_members.assert_called_once_with([queue_member.id])
        self.send_cti_event.assert_called_once_with('add_msg')

    def test_on_queue_member_updated(self):
        queue_member = Mock()
        self.cti_message_formatter.update_queue_member_config.return_value = 'update_msg'

        self.queue_member_cti_subscriber.on_queue_member_updated(queue_member)

        self.cti_message_formatter.update_queue_member_config.assert_called_once_with(queue_member)
        self.send_cti_event.assert_called_once_with('update_msg')

    def test_on_queue_member_removed(self):
        queue_member = Mock()
        queue_member.id = 'someid'
        self.cti_message_formatter.delete_queue_members.return_value = 'delete_msg'

        self.queue_member_cti_subscriber.on_queue_member_removed(queue_member)

        self.cti_message_formatter.delete_queue_members.assert_called_once_with([queue_member.id])
        self.send_cti_event.assert_called_once_with('delete_msg')
