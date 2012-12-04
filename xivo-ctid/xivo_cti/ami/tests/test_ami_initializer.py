# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import unittest

from mock import Mock
from mock import call

from xivo_cti.ami.ami_callback_handler import AMICallbackHandler
from xivo_cti.ami.initializer import AMIInitializer
from xivo_cti.xivo_ami import AMIClass


class TestAMIInitializer(unittest.TestCase):

    def setUp(self):
        self._ami_callback_handler = Mock(AMICallbackHandler)
        self.ami_initializer = AMIInitializer()
        self.ami_initializer._ami_callback_handler = self._ami_callback_handler
        self.ami_class = Mock(AMIClass)
        self.ami_initializer._ami_class = self.ami_class

    def setup_mock(self):
        self.ami_initializer._send = Mock()
        self.ami_initializer._register = Mock()
        self.ami_initializer._unregister = Mock()

    def test_register(self):
        self.setup_mock()
        self.ami_initializer.register()

        self.ami_initializer._register.assert_called_once_with('FullyBooted')

    def test_go_fully_booted(self):
        self.setup_mock()
        msg = {'Event': 'FullyBooted',
               'Privilege': 'system,all',
               'Status': 'Fully Booted'}

        self.ami_initializer.go(msg)

        self.ami_initializer._register.assert_called_once_with('CoreShowChannelsComplete')
        self.ami_initializer._send.assert_called_once_with('CoreShowChannels')
        self.assertEquals(self.ami_initializer._sent_commands, [])

    def test_send(self):
        self.ami_initializer._send('test_command')

        self.assertEquals(self.ami_initializer._sent_commands, ['test_command'])
        self.ami_class.sendcommand.assert_called_once_with('test_command', [])

    def test_go_core_show_channels_complete(self):
        self.setup_mock()
        msg = {'Event': 'CoreShowChannelsComplete',
               'EventList': 'Complete',
               'ListItems': '0'}

        self.ami_initializer.go(msg)

        self.ami_initializer._register.assert_called_once_with('RegistrationsComplete')
        self.ami_initializer._unregister.assert_called_once_with('CoreShowChannelsComplete')
        self.ami_initializer._send.assert_has_calls([call('SIPshowregistry'), call('IAXregistry')])

    def test_go_registrations_complete(self):
        self.setup_mock()
        msg = {'Event': 'RegistrationsComplete',
               'EventList': 'Complete',
               'ListItems': '0'}

        self.ami_initializer.go(msg)

        self.ami_initializer._register.assert_called_once_with('DAHDIShowChannelsComplete')
        self.ami_initializer._unregister.assert_called_once_with('RegistrationComplete')
        self.ami_initializer._send.assert_called_once_with('DAHDIShowChannels')

    def test_go_dahdi_show_channels_complete(self):
        self.setup_mock()
        msg = {'Event': 'DAHDIShowChannelsComplete',
               'Items': '0'}

        self.ami_initializer.go(msg)

        self.ami_initializer._register.assert_called_once_with('QueueSummaryComplete')
        self.ami_initializer._unregister.assert_called_once_with('DAHDIShowChannelsComplete')
        self.ami_initializer._send.assert_called_once_with('QueueSummary')

    def test_go_queue_summary_complete(self):
        self.setup_mock()
        msg = {'Event': 'QueueSummaryComplete'}

        self.ami_initializer.go(msg)

        self.ami_initializer._register.assert_called_once_with('QueueStatusComplete')
        self.ami_initializer._unregister.assert_called_once_with('QueueSummaryComplete')
        self.ami_initializer._send.assert_called_once_with('QueueStatus')

    def test_go_queue_status_complete(self):
        self.setup_mock()
        msg = {'Event': 'QueueStatusComplete'}

        self.ami_initializer.go(msg)

        self.ami_initializer._register.assert_called_once_with('ParkedCallsComplete')
        self.ami_initializer._unregister.assert_called_once_with('QueueStatusComplete')
        self.ami_initializer._send('ParkedCalls')

    def test_go_parked_calls_complete(self):
        self.setup_mock()
        msg = {'Event': 'ParkedCallsComplete',
               'Total': '0'}

        self.ami_initializer.go(msg)

        self.ami_initializer._register.assert_called_once_with('StatusComplete')
        self.ami_initializer._unregister.assert_called_once_with('ParkedCallsComplete')
        self.ami_initializer._send.assert_called_once_with('Status')

    def test_go_show_status_complete(self):
        self.setup_mock()
        msg = {'Event': 'StatusComplete',
               'Items': '0'}

        self.ami_initializer.go(msg)

        self.ami_initializer._register.assert_called_once_with('ShowDialPlanComplete')
        self.ami_initializer._unregister.assert_called_once_with('StatusComplete')
        self.ami_initializer._send.assert_called_once_with('ShowDialPlan')

    def test_go_show_dialplan_complete(self):
        self.setup_mock()
        msg = {'Event': 'ShowDialPlanComplete',
               'EventList': 'Complete',
               'ListItems': '5619',
               'ListExtensions': '1769',
               'ListPriorities': '5615',
               'ListContexts': '1769'}

        self.ami_initializer.go(msg)

        self.ami_initializer._register.assert_called_once_with('UserEvent')
        self.ami_initializer._unregister.assert_called_once_with('ShowDialPlanComplete')
        self.ami_initializer._send.assert_has_calls([call('VoicemailUsersList'),
                                                     call('MeetmeList'),
                                                     call(['UserEvent', [('UserEvent', 'InitComplete')]])])

    def test_send_userevent(self):
        self.ami_initializer._send(['UserEvent', [('UserEvent', 'My test')]])

        self.ami_class.sendcommand.assert_called_once_with('UserEvent', [('UserEvent', 'My test')])

    def test_send_go_init_complete(self):
        self.setup_mock()
        msg = {'Event': 'UserEvent',
               'Privilege': 'user,all',
               'UserEvent': 'InitComplete',
               'Action': 'UserEvent'}

        self.ami_initializer.go(msg)

        self.ami_initializer._unregister.assert_called_once_with('UserEvent')

    def test_send_go_not_init_complete(self):
        self.setup_mock()
        msg = {'Event': 'UserEvent',
               'UserEvent': 'Not init complete',
               'Privilege': 'user,all',
               'Action': 'UserEvent'}

        self.ami_initializer.go(msg)

        self.assertEqual(self.ami_initializer._unregister.call_count, 0)
