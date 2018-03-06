# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
