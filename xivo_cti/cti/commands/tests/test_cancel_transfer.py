# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.cti.commands.cancel_transfer import CancelTransfer


class TestCancelTransfer(unittest.TestCase):

    def setUp(self):
        self.commandid = 678324
        self.cancel_transfer_message = {
            'class': 'cancel_transfer',
            'commandid': self.commandid,
        }

    def test_from_dict(self):
        cancel_transfer = CancelTransfer.from_dict(self.cancel_transfer_message)

        self.assertEqual(cancel_transfer.commandid, self.commandid)
