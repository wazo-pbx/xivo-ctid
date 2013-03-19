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
from xivo_cti.cti.commands.set_user_service import EnableRecording, \
    DisableRecording
from xivo_cti.ctiserver import CTIServer
from xivo_cti.interfaces.interface_cti import CTI
from mock import Mock
from xivo_cti.cti.cti_command_handler import CTICommandHandler
from xivo_cti.cti import cti_command_registry


class TestSetUserService(unittest.TestCase):

    def setUp(self):
        pass

    def test_enable_recording(self):

        enable_recording_message = {
            'commandid': 312133,
            'class': 'featuresput',
            'function': 'enablerecording',
            'value': True,
            'target': '45'
        }

        command_classes = cti_command_registry.get_class(enable_recording_message)
        self.assertEqual(len(command_classes), 1, 'class not registered')
        self.assertEqual(EnableRecording, command_classes[0], 'invalid class registered')

        enable_recording = command_classes[0].from_dict(enable_recording_message)

        self.assertEqual(enable_recording.target, '45')

    def test_disable_recording(self):

        disable_recording_message = {
            'commandid': 312133,
            'class': 'featuresput',
            'function': 'enablerecording',
            'value': False,
            'target': '54'
        }

        command_classes = cti_command_registry.get_class(disable_recording_message)
        self.assertEqual(len(command_classes), 1, 'class not registered')
        self.assertEqual(DisableRecording, command_classes[0], 'invalid class registered')

        disable_recording = command_classes[0].from_dict(disable_recording_message)

        self.assertEqual(disable_recording.target, '54')
