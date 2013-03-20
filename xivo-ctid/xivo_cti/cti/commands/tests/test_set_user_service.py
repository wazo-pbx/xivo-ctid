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
from xivo_cti.cti.commands.set_user_service import EnableRecording, \
    DisableRecording


class TestSetUserService(unittest.TestCase):

    _disable_recording_msg = {
        'class': 'featuresput',
        'function': 'enablerecording',
        'value': False,
        'target': '54'
    }
    _enable_recording_msg = {
        'class': 'featuresput',
        'function': 'enablerecording',
        'value': True,
        'target': '45'
    }

    def test_disable_recording_msg(self):
        command = DisableRecording.from_dict(self._disable_recording_msg)

        self.assertEqual(command.target, '54')

    def test_disable_recording_registration(self):
        klass = cti_command_registry.get_class(self._disable_recording_msg)

        self.assertEqual(klass, [DisableRecording])

    def test_enable_recording_msg(self):
        command = EnableRecording.from_dict(self._enable_recording_msg)

        self.assertEqual(command.target, '45')

    def test_enable_recording_registration(self):
        klass = cti_command_registry.get_class(self._enable_recording_msg)

        self.assertEqual(klass, [EnableRecording])
