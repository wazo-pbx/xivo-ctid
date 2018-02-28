# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.cti.commands.hangup import Hangup


class TestHangup(unittest.TestCase):

    def setUp(self):
        self.commandid = 125731893
        self.hangup_message = {
            'class': 'hangup',
            'commandid': self.commandid,
            'ipbxid': 'xivo',
            'userid': '1'
        }

    def test_from_dict(self):
        hangup = Hangup.from_dict(self.hangup_message)

        self.assertEqual(hangup.commandid, self.commandid)
