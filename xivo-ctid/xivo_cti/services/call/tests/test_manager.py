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
from xivo_cti.services.call.manager import CallManager
from xivo_cti.services.call.notifier import CallNotifier
from xivo_cti.services.call.storage import CallStorage
from xivo_cti.model.line_status import LineStatus
from xivo.asterisk.extension import Extension


class TestCallManager(unittest.TestCase):

    def setUp(self):
        self.call_storage = Mock(CallStorage)
        self.call_notifier = Mock(CallNotifier)
        self.call_manager = CallManager(self.call_storage, self.call_notifier)

    @patch('xivo_dao.line_dao.get_extension_from_interface')
    def test_handle_newstate(self, get_extension_from_interface):
        interface = 'SIP/abcd'
        extension = Extension('1000', 'default')
        channel = "%s-00001" % interface
        call_status = LineStatus.ringing

        get_extension_from_interface.return_value = extension

        ami_event = {
            'Event': 'Newstate',
            'ChannelState': '5',
            'Channel': channel,
        }

        self.call_manager.handle_newstate(ami_event)

        self.call_storage.update_line_status.assert_called_once_with(extension, call_status)
        get_extension_from_interface.assert_called_once_with(interface)

    @patch('xivo_dao.line_dao.get_extension_from_interface')
    def test_handle_hangup(self, get_extension_from_interface):
        interface = 'SIP/abcd'
        extension = Extension('1000', 'default')
        channel = "%s-00001" % interface
        call_status = LineStatus.available

        get_extension_from_interface.return_value = extension

        ami_event = {
            'Event': 'Hangup',
            'Channel': channel,
        }

        self.call_manager.handle_hangup(ami_event)

        self.call_storage.update_line_status.assert_called_once_with(extension, call_status)
        get_extension_from_interface.assert_called_once_with(interface)
