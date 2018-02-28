# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.cti.commands.hold_switchboard import HoldSwitchboard


class TestHoldSwitchboard(unittest.TestCase):

    def setUp(self):
        self.commandid = 125731893
        self.queue_name = 'hold_queue'
        self.hold_switchboard_message = {
            'class': 'hold_switchboard',
            'commandid': self.commandid,
            'queue_name': self.queue_name,
        }

    def test_from_dict(self):
        hold_switchboard = HoldSwitchboard.from_dict(self.hold_switchboard_message)

        self.assertEqual(hold_switchboard.commandid, self.commandid)
