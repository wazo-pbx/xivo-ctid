# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.cti.commands.direct_transfer import DirectTransfer


class TestDirectTransfer(unittest.TestCase):

    def setUp(self):
        self.commandid = 5664346
        self.number = '5431'
        self.direct_transfer_message = {
            'class': 'direct_transfer',
            'commandid': self.commandid,
            'number': self.number,
        }

    def test_from_dict(self):
        direct_transfer = DirectTransfer.from_dict(self.direct_transfer_message)

        self.assertEqual(direct_transfer.commandid, self.commandid)
        self.assertEqual(direct_transfer.number, self.number)
