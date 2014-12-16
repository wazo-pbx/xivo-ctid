# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

from xivo_cti.services.queue_entry_notifier import QueueEntryNotifier
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.cti.cti_group import CTIGroup, CTIGroupFactory

QUEUE_NAME_1, QUEUE_ID_1 = 'testqueue', 1


class TestQueueEntryNotifier(unittest.TestCase):

    def setUp(self):
        self.cti_group = Mock(CTIGroup)
        self.cti_group_factory = Mock(CTIGroupFactory)
        self.cti_group_factory.new_cti_group.return_value = self.cti_group
        self.notifier = QueueEntryNotifier(self.cti_group_factory)

    @patch('xivo_dao.queue_dao.queue_name', return_value=QUEUE_NAME_1)
    def test_subscribe_and_publish(self, mock_queue_name):
        connection = Mock(CTI)
        new_state = 'queue_1_entries'

        self.notifier.subscribe(connection, QUEUE_ID_1)
        self.notifier.publish(QUEUE_NAME_1, new_state)

        self.cti_group.add.assert_called_once_with(connection)
        self.cti_group.send_message.assert_called_once_with(new_state)

    @patch('xivo_dao.queue_dao.queue_name', return_value=QUEUE_NAME_1)
    def test_subscribe_after_message(self, mock_queue_name):
        connection_1 = Mock(CTI)
        new_state = 'queue_1_entries'

        self.notifier.publish(QUEUE_NAME_1, new_state)

        self.assertEquals(connection_1.send_message.call_count, 0)

        self.notifier.subscribe(connection_1, QUEUE_ID_1)

        connection_1.send_message.assert_called_once_with(new_state)
