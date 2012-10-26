#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from mock import Mock, patch

from xivo_cti.services.queue_entry_notifier import QueueEntryNotifier
from xivo_cti.interfaces.interface_cti import CTI

QUEUE_NAME_1, QUEUE_ID_1 = 'testqueue', 1
QUEUE_NAME_2, QUEUE_ID_2 = 'anothertestqueue', 2


class TestQueueEntryNotifier(unittest.TestCase):

    def setUp(self):
        self.notifier = QueueEntryNotifier()

    @patch('xivo_dao.queue_features_dao.queue_name')
    def test_subscribe(self, mock_queue_name):
        connection_1 = Mock(CTI)
        connection_2 = Mock(CTI)

        mock_queue_name.return_value = QUEUE_NAME_1
        self.notifier.subscribe(connection_1, QUEUE_ID_1)
        mock_queue_name.return_value = QUEUE_NAME_2
        self.notifier.subscribe(connection_2, QUEUE_ID_2)

        subscriptions = self.notifier._subscriptions[QUEUE_NAME_1]

        self.assertTrue(connection_1 in subscriptions)
        self.assertTrue(connection_2 not in subscriptions)

        subscriptions_2 = self.notifier._subscriptions[QUEUE_NAME_2]

        self.assertTrue(connection_2 in subscriptions_2)

    @patch('xivo_dao.queue_features_dao.queue_name', return_value=QUEUE_NAME_1)
    def test_publish(self, mock_queue_name):
        new_state = 'queue_1_entries'
        connection_1 = Mock(CTI)
        self.notifier.subscribe(connection_1, QUEUE_ID_1)

        self.notifier.publish(QUEUE_NAME_1, new_state)

        connection_1.send_message.assert_called_once_with(new_state)

    @patch('xivo_dao.queue_features_dao.queue_name', return_value=QUEUE_NAME_1)
    def test_subscribe_after_message(self, mock_queue_name):
        connection_1 = Mock(CTI)
        new_state = 'queue_1_entries'

        self.notifier.publish(QUEUE_NAME_1, new_state)

        self.assertEquals(connection_1.send_message.call_count, 0)

        self.notifier.subscribe(connection_1, QUEUE_ID_1)

        connection_1.send_message.assert_called_once_with(new_state)
