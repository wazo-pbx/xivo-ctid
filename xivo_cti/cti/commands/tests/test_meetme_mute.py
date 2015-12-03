# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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
