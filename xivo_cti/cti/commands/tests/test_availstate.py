# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from xivo_cti.cti.commands.availstate import Availstate


class TestAvailstate(unittest.TestCase):

    def setUp(self):
        self.commandid = 125731893
        self.outtolunch = {'availstate': 'outtolunch',
                           'class': 'availstate',
                           'commandid': self.commandid,
                           'ipbxid': 'xivo',
                           'userid': '1'}

    def test_from_dict(self):
        availstate = Availstate.from_dict(self.outtolunch)

        self.assertEqual(availstate.availstate, 'outtolunch')
        self.assertEqual(availstate.commandid, self.commandid)
