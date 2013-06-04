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

from mock import patch, Mock
from xivo.asterisk.extension import Extension
from xivo_cti.model.endpoint_status import EndpointStatus
from xivo_cti.model.call_event import CallEvent
from xivo_cti.services.call.notifier import CallNotifier
from xivo_cti.services.call.storage import CallStorage


class TestCallStorage(unittest.TestCase):

    def setUp(self):
        self.notifier = Mock(CallNotifier)
        self.storage = CallStorage(self.notifier)

    def test_update_endpoint_status(self):
        extension = Extension('1234', 'my_context')
        status = EndpointStatus.ringing
        expected_event = CallEvent(extension, status)

        self.storage.update_endpoint_status(extension, status)

        self.notifier.notify.assert_called_once_with(expected_event)
