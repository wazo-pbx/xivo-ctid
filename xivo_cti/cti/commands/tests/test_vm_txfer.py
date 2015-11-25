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

from .. import vm_txfer


class TestBlindTransferVoicemail(unittest.TestCase):

    def test_from_dict(self):
        msg = vm_txfer.BlindTransferVoicemail.from_dict({'class': 'blind_transfer_voicemail',
                                                         'voicemail': '1005'})

        self.assertEqual(msg.voicemail_number, '1005')

    def test_that_an_invalid_vm_number_raises(self):
        invalid_values = [
            'foobar',
            '',
            124,
            '''1002
            ''',
            '1002\r\n\r\nEvent: test'
        ]

        for v in invalid_values:
            self.assertRaises(ValueError,
                              vm_txfer.BlindTransferVoicemail.from_dict,
                              {'class': 'blind_transfer_voicemail',
                               'voicemail': v})
