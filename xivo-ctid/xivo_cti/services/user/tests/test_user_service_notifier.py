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
# contracted with Avencall. See the LICENSE file at top of the source tree
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
from xivo_cti.services.user.notifier import UserServiceNotifier
from mock import Mock


class TestUserServiceNotifier(unittest.TestCase):

    def setUp(self):
        self.ipbx_id = 'xivo'
        self.notifier = UserServiceNotifier()
        self.notifier.send_cti_event = Mock()
        self.notifier.ipbx_id = self.ipbx_id

    def tearDown(self):
        pass

    def test_dnd_enabled(self):
        user_id = 34
        ipbx_id = 'xivo'
        notifier = UserServiceNotifier()
        notifier.send_cti_event = Mock()
        notifier.ipbx_id = ipbx_id
        expected = {"class": "getlist",
                    "config": {"enablednd": True},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": ipbx_id}

        notifier.dnd_enabled(user_id)

        notifier.send_cti_event.assert_called_once_with(expected)

    def test_dnd_disabled(self):
        user_id = 34
        ipbx_id = 'xivo'
        notifier = UserServiceNotifier()
        notifier.send_cti_event = Mock()
        notifier.ipbx_id = ipbx_id
        expected = {"class": "getlist",
                    "config": {"enablednd": False},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": ipbx_id}

        notifier.dnd_disabled(user_id)

        notifier.send_cti_event.assert_called_once_with(expected)

    def test_filter_enabled(self):
        user_id = 32

        expected = {"class": "getlist",
                    "config": {"incallfilter": True},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.filter_enabled(user_id)

        self.notifier.send_cti_event.assert_called_once_with(expected)

    def test_filter_disabled(self):
        user_id = 932

        expected = {"class": "getlist",
                    "config": {"incallfilter": False},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.filter_disabled(user_id)

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

        self.notifier.presence_updated(user_id, 'available')

        self.notifier.send_cti_event.assert_called_once_with(expected)
