# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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
from xivo_cti.cti.commands.set_user_service import DisableDND, \
    EnableDND, EnableRecording, DisableRecording, EnableFilter, DisableFilter


class TestSetUserService(unittest.TestCase):

    _enable_dnd_msg = {
        'class': 'featuresput',
        'function': 'enablednd',
        'value': True,
    }
    _disable_dnd_msg = {
        'class': 'featuresput',
        'function': 'enablednd',
        'value': False,
    }
    _enable_filter_msg = {
        'class': 'featuresput',
        'function': 'incallfilter',
        'value': True,
    }
    _disable_filter_msg = {
        'class': 'featuresput',
        'function': 'incallfilter',
        'value': False,
    }
    _enable_recording_msg = {
        'class': 'featuresput',
        'function': 'enablerecording',
        'value': True,
        'target': '45'
    }
    _disable_recording_msg = {
        'class': 'featuresput',
        'function': 'enablerecording',
        'value': False,
        'target': '54'
    }

    def test_enable_dnd_msg_no_exception(self):
        EnableDND.from_dict(self._enable_dnd_msg)

    def test_enable_dnd_registration(self):
        klass = cti_command_registry.get_class(self._enable_dnd_msg)

        self.assertEqual(klass, [EnableDND])

    def test_disable_dnd_msg_no_exception(self):
        DisableDND.from_dict(self._disable_dnd_msg)

    def test_disable_dnd_registration(self):
        klass = cti_command_registry.get_class(self._disable_dnd_msg)

        self.assertEqual(klass, [DisableDND])

    def test_enable_filter_msg_no_exception(self):
        EnableFilter.from_dict(self._enable_filter_msg)

    def test_enable_filter_registration(self):
        klass = cti_command_registry.get_class(self._enable_filter_msg)

        self.assertEqual(klass, [EnableFilter])

    def test_disable_filter_msg_no_exception(self):
        DisableFilter.from_dict(self._disable_filter_msg)

    def test_disable_filter_registration(self):
        klass = cti_command_registry.get_class(self._disable_filter_msg)

        self.assertEqual(klass, [DisableFilter])

    def test_enable_recording_msg(self):
        command = EnableRecording.from_dict(self._enable_recording_msg)

        self.assertEqual(command.target, '45')

    def test_enable_recording_registration(self):
        klass = cti_command_registry.get_class(self._enable_recording_msg)

        self.assertEqual(klass, [EnableRecording])

    def test_disable_recording_msg(self):
        command = DisableRecording.from_dict(self._disable_recording_msg)

        self.assertEqual(command.target, '54')

    def test_disable_recording_registration(self):
        klass = cti_command_registry.get_class(self._disable_recording_msg)

        self.assertEqual(klass, [DisableRecording])
