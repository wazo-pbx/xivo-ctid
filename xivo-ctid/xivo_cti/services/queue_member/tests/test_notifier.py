# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_cti.services.queue_member.notifier import QueueMemberNotifier


class TestQueueMemberNotifier(unittest.TestCase):

    def setUp(self):
        self.queue_member_notifier = QueueMemberNotifier()

    def test_subscribe_to_queue_member_add(self):
        callback = Mock()
        queue_member = Mock()

        self.queue_member_notifier.subscribe_to_queue_member_add(callback)
        self.queue_member_notifier._on_queue_member_added(queue_member)

        callback.assert_called_once_with(queue_member)

    def test_subscribe_to_queue_member_update(self):
        callback = Mock()
        queue_member = Mock()

        self.queue_member_notifier.subscribe_to_queue_member_update(callback)
        self.queue_member_notifier._on_queue_member_updated(queue_member)

        callback.assert_called_once_with(queue_member)

    def test_subscribe_to_queue_member_remove(self):
        callback = Mock()
        queue_member = Mock()

        self.queue_member_notifier.subscribe_to_queue_member_remove(callback)
        self.queue_member_notifier._on_queue_member_removed(queue_member)

        callback.assert_called_once_with(queue_member)
