# -*- coding: utf-8 -*-

# Copyright (C) 2013  Avencall
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
from xivo_cti.cti import cti_command_registry
from xivo_cti.cti.commands.set_forward import DisableBusyForward, \
    DisableNoAnswerForward, DisableUnconditionalForward, EnableBusyForward, \
    EnableNoAnswerForward, EnableUnconditionalForward


class TestSetForward(unittest.TestCase):

    _destination = '1984'

    _disable_busy_msg = {
        "class": "featuresput",
        "function": "fwd",
        "value": {'destbusy': _destination, 'enablebusy': False}
    }
    _disable_no_answer_msg = {
        "class": "featuresput",
        "function": "fwd",
        "value": {'destrna': _destination, 'enablerna': False}
    }
    _disable_unc_msg = {
        "class": "featuresput",
        "function": "fwd",
        "value": {'destunc': _destination, 'enableunc': False}
    }
    _enable_busy_msg = {
        "class": "featuresput",
        "function": "fwd",
        "value": {'destbusy': _destination, 'enablebusy': True}
    }
    _enable_no_answer_msg = {
        "class": "featuresput",
        "function": "fwd",
        "value": {'destrna': _destination, 'enablerna': True}
    }
    _enable_unc_msg = {
        "class": "featuresput",
        "function": "fwd",
        "value": {'destunc': _destination, 'enableunc': True}
    }

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

    def test_disable_unc_msg(self):
        command = DisableUnconditionalForward.from_dict(self._disable_unc_msg)

        self.assertEqual(command.destination, self._destination)

    def test_disable_unc_registration(self):
        klass = cti_command_registry.get_class(self._disable_unc_msg)

        self.assertEqual(klass, [DisableUnconditionalForward])

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

    def test_enable_unc_msg(self):
        command = EnableUnconditionalForward.from_dict(self._enable_unc_msg)

        self.assertEqual(command.destination, self._destination)

    def test_enable_unc_registration(self):
        klass = cti_command_registry.get_class(self._enable_unc_msg)

        self.assertEqual(klass, [EnableUnconditionalForward])
