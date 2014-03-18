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
from xivo_cti.model.endpoint_event import EndpointEvent
from xivo_cti.services.call.endpoint_notifier import EndpointNotifier


NUMBER = '2573'
CONTEXT = 'my_context'
EXTENSION = Mock(number=NUMBER, context=CONTEXT)
CALLBACK = Mock()


class TestEndpointNotifier(unittest.TestCase):

    def setUp(self):
        self.pubsub = Mock()
        self.notifier = EndpointNotifier(self.pubsub)

    def test_subscribe_to_status_changes(self):
        self.notifier.subscribe_to_status_changes(EXTENSION, CALLBACK)

        self.pubsub.subscribe.assert_called_once_with(('status', EXTENSION), CALLBACK)

    def test_unsubscribe_from_status_changes(self):
        self.notifier.unsubscribe_from_status_changes(EXTENSION, CALLBACK)

        self.pubsub.unsubscribe.assert_called_once_with(('status', EXTENSION), CALLBACK)

    def test_notify(self):
        event = Mock(EndpointEvent)
        event.extension = EXTENSION

        self.notifier.notify(event)

        self.pubsub.publish.assert_called_once_with(('status', EXTENSION), event)
