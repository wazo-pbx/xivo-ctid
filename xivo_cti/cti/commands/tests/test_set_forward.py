# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from xivo_cti.cti import cti_command_registry
from xivo_cti.cti.commands.set_forward import DisableBusyForward, \
    DisableNoAnswerForward, DisableUnconditionalForward, EnableBusyForward, \
    EnableNoAnswerForward, EnableUnconditionalForward


class TestSetForward(unittest.TestCase):

    _destination = '1984'

    _enable_busy_msg = {
        "class": "featuresput",
        "function": "fwd",
        "value": {'destbusy': _destination, 'enablebusy': True}
    }
    _disable_busy_msg = {
        "class": "featuresput",
        "function": "fwd",
        "value": {'destbusy': _destination, 'enablebusy': False}
    }
    _enable_no_answer_msg = {
        "class": "featuresput",
        "function": "fwd",
        "value": {'destrna': _destination, 'enablerna': True}
    }
    _disable_no_answer_msg = {
        "class": "featuresput",
        "function": "fwd",
        "value": {'destrna': _destination, 'enablerna': False}
    }
    _enable_unc_msg = {
        "class": "featuresput",
        "function": "fwd",
        "value": {'destunc': _destination, 'enableunc': True}
    }
    _disable_unc_msg = {
        "class": "featuresput",
        "function": "fwd",
        "value": {'destunc': _destination, 'enableunc': False}
    }

    def test_enable_busy_msg(self):
        command = EnableBusyForward.from_dict(self._enable_busy_msg)

        self.assertEqual(command.destination, self._destination)

    def test_enable_busy_registration(self):
        klass = cti_command_registry.get_class(self._enable_busy_msg)

        self.assertEqual(klass, [EnableBusyForward])

    def test_enable_no_answer_msg(self):
        command = EnableNoAnswerForward.from_dict(self._enable_no_answer_msg)

        self.assertEqual(command.destination, self._destination)

    def test_enable_no_answer_registration(self):
        klass = cti_command_registry.get_class(self._enable_no_answer_msg)

        self.assertEqual(klass, [EnableNoAnswerForward])

    def test_disable_busy_msg(self):
        command = DisableBusyForward.from_dict(self._disable_busy_msg)

        self.assertEqual(command.destination, self._destination)

    def test_disable_busy_registration(self):
        klass = cti_command_registry.get_class(self._disable_busy_msg)

        self.assertEqual(klass, [DisableBusyForward])

    def test_disable_no_answer_msg(self):
        command = DisableNoAnswerForward.from_dict(self._disable_no_answer_msg)

        self.assertEqual(command.destination, self._destination)

    def test_disable_no_answer_registration(self):
        klass = cti_command_registry.get_class(self._disable_no_answer_msg)

        self.assertEqual(klass, [DisableNoAnswerForward])

    def test_enable_unc_msg(self):
        command = EnableUnconditionalForward.from_dict(self._enable_unc_msg)

        self.assertEqual(command.destination, self._destination)

    def test_enable_unc_registration(self):
        klass = cti_command_registry.get_class(self._enable_unc_msg)

        self.assertEqual(klass, [EnableUnconditionalForward])

    def test_disable_unc_msg(self):
        command = DisableUnconditionalForward.from_dict(self._disable_unc_msg)

        self.assertEqual(command.destination, self._destination)

    def test_disable_unc_registration(self):
        klass = cti_command_registry.get_class(self._disable_unc_msg)

        self.assertEqual(klass, [DisableUnconditionalForward])
