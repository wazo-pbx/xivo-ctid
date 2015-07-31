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
from xivo.pubsub import Pubsub
from xivo_cti.model.call_status import CallStatus
from xivo_cti.model.call_event import CallEvent
from xivo_cti.services.call.call_notifier import CallNotifier


NUMBER = '2587'
CONTEXT = 'my_context'
EXTENSION = Mock(number=NUMBER, context=CONTEXT)
CALLBACK = Mock()


class TestCallNotifier(unittest.TestCase):

    def setUp(self):
        self.pubsub = Mock(Pubsub)
        self.notifier = CallNotifier(self.pubsub)

    def test_subscribe_to_incoming_call_events(self):
        self.notifier.subscribe_to_incoming_call_events(EXTENSION, CALLBACK)

        self.pubsub.subscribe.assert_called_once_with(('calls_incoming', EXTENSION), CALLBACK)

    def test_subscribe_to_outgoing_call_events(self):
        self.notifier.subscribe_to_outgoing_call_events(EXTENSION, CALLBACK)

        self.pubsub.subscribe.assert_called_once_with(('calls_outgoing', EXTENSION), CALLBACK)

    def test_unsubscribe_from_incoming_call_events(self):
        self.notifier.unsubscribe_from_incoming_call_events(EXTENSION, CALLBACK)

        self.pubsub.unsubscribe.assert_called_once_with(('calls_incoming', EXTENSION), CALLBACK)

    def test_unsubscribe_from_ougoing_call_events(self):
        self.notifier.unsubscribe_from_outgoing_call_events(EXTENSION, CALLBACK)

        self.pubsub.unsubscribe.assert_called_once_with(('calls_outgoing', EXTENSION), CALLBACK)

    def test_notify(self):
        uniqueid = '2938749837.34'
        source = Mock(number=NUMBER, context=CONTEXT)
        destination = Mock(number=NUMBER, context=CONTEXT)
        status = CallStatus.ringing
        event = CallEvent(uniqueid, source, destination, status)

        self.notifier.notify(event)

        self.assertEquals(self.pubsub.publish.call_count, 2)
        self.pubsub.publish.assert_any_call(('calls_outgoing', source), event)
        self.pubsub.publish.assert_any_call(('calls_incoming', destination), event)
