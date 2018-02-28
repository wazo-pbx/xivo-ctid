# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock, patch
from xivo_cti.services.queue_member.cti.subscriber import QueueMemberCTISubscriber


@patch('xivo_cti.services.queue_member.cti.subscriber.CTIMessageFormatter')
class TestQueueMemberCTISubscriber(unittest.TestCase):

    def setUp(self):
        self.send_cti_event = Mock()
        self.queue_member_cti_subscriber = QueueMemberCTISubscriber()
        self.queue_member_cti_subscriber.send_cti_event = self.send_cti_event

    def test_on_queue_member_added(self, message_formatter):
        queue_member = Mock()
        queue_member.id = 'someid'
        message_formatter.add_queue_members.return_value = 'add_msg'

        self.queue_member_cti_subscriber.on_queue_member_added(queue_member)

        message_formatter.add_queue_members.assert_called_once_with([queue_member.id])
        self.send_cti_event.assert_called_once_with('add_msg')

    def test_on_queue_member_updated(self, message_formatter):
        queue_member = Mock()
        message_formatter.update_queue_member_config.return_value = 'update_msg'

        self.queue_member_cti_subscriber.on_queue_member_updated(queue_member)

        message_formatter.update_queue_member_config.assert_called_once_with(queue_member)
        self.send_cti_event.assert_called_once_with('update_msg')

    def test_on_queue_member_removed(self, message_formatter):
        queue_member = Mock()
        queue_member.id = 'someid'
        message_formatter.delete_queue_members.return_value = 'delete_msg'

        self.queue_member_cti_subscriber.on_queue_member_removed(queue_member)

        message_formatter.delete_queue_members.assert_called_once_with([queue_member.id])
        self.send_cti_event.assert_called_once_with('delete_msg')
