# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
from xivo.asterisk.extension import Extension
from xivo_cti.model.endpoint_event import EndpointEvent
from xivo_cti.services.call.endpoint_notifier import EndpointNotifier


class TestEndpointNotifier(unittest.TestCase):

    def setUp(self):
        self.pubsub = Mock()
        self.notifier = EndpointNotifier(self.pubsub)

    def test_subscribe_to_status_changes(self):
        callback = Mock()
        extension = Extension('1000', 'my_context')

        self.notifier.subscribe_to_status_changes(extension, callback)

        self.pubsub.subscribe.assert_called_once_with(('status', extension), callback)

    def test_unsubscribe_from_status_changes(self):
        callback = Mock()
        extension = Extension('1000', 'my_context')

        self.notifier.unsubscribe_from_status_changes(extension, callback)

        self.pubsub.unsubscribe.assert_called_once_with(('status', extension), callback)

    def test_notify(self):
        extension = Extension('1000', 'my_context')
        event = Mock(EndpointEvent)
        event.extension = extension

        self.notifier.notify(event)

        self.pubsub.publish.assert_called_once_with(('status', extension), event)
