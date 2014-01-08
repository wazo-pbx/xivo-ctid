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
from xivo_cti.cti import cti_command_registry
from xivo_cti.cti.commands.subscribe import SubscribeCurrentCalls, \
    SubscribeMeetmeUpdate, SubscribeQueueEntryUpdate


class TestSubscribe(unittest.TestCase):

    _queueid = '42'

    _current_calls_msg = {
        'class': 'subscribe',
        'message': 'current_calls',
    }
    _meetme_update_msg = {
        'class': 'subscribe',
        'message': 'meetme_update',
    }
    _queueentryupdate_msg = {
        'class': 'subscribe',
        'message': 'queueentryupdate',
        'queueid': _queueid,
    }

    def test_current_calls_msg(self):
        command = SubscribeCurrentCalls.from_dict(self._current_calls_msg)

        self.assertEqual(command.message, 'current_calls')

    def test_current_calls_registration(self):
        klass = cti_command_registry.get_class(self._current_calls_msg)

        self.assertEqual(klass, [SubscribeCurrentCalls])

    def test_meetme_update_msg(self):
        command = SubscribeMeetmeUpdate.from_dict(self._meetme_update_msg)

        self.assertEqual(command.message, 'meetme_update')

    def test_meetme_update_registration(self):
        klass = cti_command_registry.get_class(self._meetme_update_msg)

        self.assertEqual(klass, [SubscribeMeetmeUpdate])

    def test_queueentryupdate_msg(self):
        command = SubscribeQueueEntryUpdate.from_dict(self._queueentryupdate_msg)

        self.assertEqual(command.message, 'queueentryupdate')
        self.assertEqual(command.queue_id, int(self._queueid))

    def test_queueentryupdate_registration(self):
        klass = cti_command_registry.get_class(self._queueentryupdate_msg)

        self.assertEqual(klass, [SubscribeQueueEntryUpdate])
