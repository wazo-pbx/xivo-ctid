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
