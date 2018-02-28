# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import sentinel

from xivo_cti.cti.commands.meetme_mute import MeetmeMute


class TestMeetmeMute(unittest.TestCase):

    def setUp(self):
        self.message = {
            'class': 'ipbxcommand',
            'command': 'meetme',
            'function': 'MeetmeMute',
            'functionargs': ['1001', '3'],
            'commandid': sentinel.commandid,
        }

    def test_from_dict(self):
        meetme_mute = MeetmeMute.from_dict(self.message)

        self.assertEqual(meetme_mute.meetme_number, '1001')
        self.assertEqual(meetme_mute.user_position, '3')

    def test_ami_injection(self):
        self.assertRaises(ValueError, MeetmeMute.from_dict, {'class': 'ipbxcommand',
                                                             'command': 'meetme',
                                                             'function': 'MeetmeMute',
                                                             'functionargs': [
                                                                 '1001', '3\r\n\r\nCommand: Command\r\n\r\n'
                                                             ],
                                                             'commandid': sentinel.commandid})
