# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.cti.commands.attended_transfer import AttendedTransfer


class TestAttendedTransfer(unittest.TestCase):

    def setUp(self):
        self.commandid = 5664346
        self.number = '1234'
        self.attended_transfer_message = {
            'class': 'attended_transfer',
            'commandid': self.commandid,
            'number': self.number,
        }

    def test_from_dict(self):
        attended_transfer = AttendedTransfer.from_dict(self.attended_transfer_message)

        self.assertEqual(attended_transfer.commandid, self.commandid)
        self.assertEqual(attended_transfer.number, self.number)
