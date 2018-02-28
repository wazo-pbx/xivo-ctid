# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.cti.commands.listen import Listen


class TestListen(unittest.TestCase):

    def setUp(self):
        self.commandid = 125731893
        self.destination = 'xivo/42'
        self.message = {
            'class': 'ipbxcommand',
            'command': 'listen',
            'subcommand': 'start',
            'destination': self.destination,
        }

    def test_from_dict(self):
        listen = Listen.from_dict(self.message)

        self.assertEqual(listen.destination, self.destination)
