# -*- coding: utf-8 -*-

# Copyright (C) 2007-2016 Avencall
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

from xivo_cti.services.user.notifier import UserServiceNotifier
from xivo_cti.services.user.notifier import UserStatusUpdateEvent


class TestUserServiceNotifier(unittest.TestCase):

    def setUp(self):
        self.ipbx_id = 'xivo'
        self.bus_publisher = Mock()
        self.notifier = UserServiceNotifier(self.bus_publisher)
        self.notifier.send_cti_event = Mock()
        self.notifier.ipbx_id = self.ipbx_id

    def test_dnd_enabled_true(self):
        user_id = 34
        expected = {"class": "getlist",
                    "config": {"enablednd": True},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.dnd_enabled(user_id, True)

        self.notifier.send_cti_event.assert_called_once_with(expected)

    def test_dnd_disabled_false(self):
        user_id = 34
        expected = {"class": "getlist",
                    "config": {"enablednd": False},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.dnd_enabled(user_id, False)

        self.notifier.send_cti_event.assert_called_once_with(expected)

    def test_incallfilter_enabled_true(self):
        user_id = 32

        expected = {"class": "getlist",
                    "config": {"incallfilter": True},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.incallfilter_enabled(user_id, True)

        self.notifier.send_cti_event.assert_called_once_with(expected)

    def test_incallfilter_disabled_false(self):
        user_id = 932

        expected = {"class": "getlist",
                    "config": {"incallfilter": False},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.incallfilter_enabled(user_id, False)

        self.notifier.send_cti_event.assert_called_once_with(expected)

    def test_unconditional_fwd_enabled(self):
        user_id = 456
        destination = '234'
        expected = {"class": "getlist",
                    "config": {"enableunc": True,
                               'destunc': destination},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.unconditional_fwd_enabled(user_id, destination)

        self.notifier.send_cti_event.assert_called_once_with(expected)

    def test_rna_fwd_enabled(self):
        user_id = 456
        destination = '234'
        expected = {"class": "getlist",
                    "config": {"enablerna": True,
                               'destrna': destination},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.rna_fwd_enabled(user_id, destination)

        self.notifier.send_cti_event.assert_called_once_with(expected)

    def test_rna_fwd_disabled(self):
        user_id = 456
        destination = '234'
        expected = {"class": "getlist",
                    "config": {"enablerna": False,
                               'destrna': destination},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.rna_fwd_disabled(user_id, destination)

        self.notifier.send_cti_event.assert_called_once_with(expected)

    def test_busy_fwd_enabled(self):
        user_id = 456
        destination = '234'
        expected = {"class": "getlist",
                    "config": {"enablebusy": True,
                               'destbusy': destination},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.busy_fwd_enabled(user_id, destination)

        self.notifier.send_cti_event.assert_called_once_with(expected)

    def test_busy_fwd_disabled(self):
        user_id = 456
        destination = '234'
        expected = {"class": "getlist",
                    "config": {"enablebusy": False,
                               'destbusy': destination},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.busy_fwd_disabled(user_id, destination)

        self.notifier.send_cti_event.assert_called_once_with(expected)

    def test_presence_updated(self):
        user_id = 64
        expected = {"class": "getlist",
                    "status": {"availstate": 'available'},
                    "function": "updatestatus",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}
        self.notifier._send_bus_event = Mock()

        self.notifier.presence_updated(user_id, 'available')

        self.notifier.send_cti_event.assert_called_once_with(expected)
        expected_event = UserStatusUpdateEvent(user_id, 'available')
        self.bus_publisher.publish.assert_called_once_with(expected_event)

    def test_recording_enabled(self):
        user_id = 42
        expected = {"class": "getlist",
                    "config": {"enablerecording": True},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.recording_enabled(user_id)

        self.notifier.send_cti_event.assert_called_once_with(expected)

    def test_recording_disabled(self):
        user_id = 54
        expected = {"class": "getlist",
                    "config": {"enablerecording": False},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.recording_disabled(user_id)

        self.notifier.send_cti_event.assert_called_once_with(expected)
