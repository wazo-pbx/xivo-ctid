# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.cti.commands.complete_transfer import CompleteTransfer


class TestCompleteTransfer(unittest.TestCase):

    def setUp(self):
        self.commandid = 678324
        self.complete_transfer_message = {
            'class': 'complete_transfer',
            'commandid': self.commandid,
        }

    def test_from_dict(self):
        complete_transfer = CompleteTransfer.from_dict(self.complete_transfer_message)

        self.assertEqual(complete_transfer.commandid, self.commandid)
