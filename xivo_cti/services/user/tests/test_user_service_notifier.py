# -*- coding: utf-8 -*-
# Copyright (C) 2007-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from xivo_cti.services.user.notifier import UserServiceNotifier


class TestUserServiceNotifier(unittest.TestCase):

    def setUp(self):
        self.ipbx_id = 'xivo'
        self.notifier = UserServiceNotifier()
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

    def test_dnd_enabled_false(self):
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

    def test_incallfilter_enabled_false(self):
        user_id = 932

        expected = {"class": "getlist",
                    "config": {"incallfilter": False},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.incallfilter_enabled(user_id, False)

        self.notifier.send_cti_event.assert_called_once_with(expected)

    def test_unconditional_fwd_enabled_true(self):
        user_id = 456
        destination = '234'
        expected = {"class": "getlist",
                    "config": {"enableunc": True,
                               'destunc': destination},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.unconditional_fwd_enabled(user_id, True, destination)

        self.notifier.send_cti_event.assert_called_once_with(expected)

    def test_rna_fwd_enabled_true(self):
        user_id = 456
        destination = '234'
        expected = {"class": "getlist",
                    "config": {"enablerna": True,
                               'destrna': destination},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.rna_fwd_enabled(user_id, True, destination)

        self.notifier.send_cti_event.assert_called_once_with(expected)

    def test_rna_fwd_enabled_false(self):
        user_id = 456
        destination = '234'
        expected = {"class": "getlist",
                    "config": {"enablerna": False,
                               'destrna': destination},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.rna_fwd_enabled(user_id, False, destination)

        self.notifier.send_cti_event.assert_called_once_with(expected)

    def test_busy_fwd_enabled_true(self):
        user_id = 456
        destination = '234'
        expected = {"class": "getlist",
                    "config": {"enablebusy": True,
                               'destbusy': destination},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.busy_fwd_enabled(user_id, True, destination)

        self.notifier.send_cti_event.assert_called_once_with(expected)

    def test_busy_fwd_enabled_false(self):
        user_id = 456
        destination = '234'
        expected = {"class": "getlist",
                    "config": {"enablebusy": False,
                               'destbusy': destination},
                    "function": "updateconfig",
                    "listname": "users",
                    "tid": user_id,
                    "tipbxid": self.ipbx_id}

        self.notifier.busy_fwd_enabled(user_id, False, destination)

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
