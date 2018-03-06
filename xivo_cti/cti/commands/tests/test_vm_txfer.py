# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from .. import vm_txfer


class TestBlindTransferVoicemail(unittest.TestCase):

    def test_from_dict(self):
        msg = vm_txfer.BlindTransferVoicemail.from_dict({'class': 'blind_transfer_voicemail',
                                                         'voicemail': '1005'})

        self.assertEqual(msg.voicemail_number, '1005')

    def test_that_an_invalid_vm_number_raises(self):
        invalid_values = [
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
