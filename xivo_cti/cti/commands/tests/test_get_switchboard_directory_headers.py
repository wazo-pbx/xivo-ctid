# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.cti.commands.get_switchboard_directory_headers import GetSwitchboardDirectoryHeaders


class TestGetSwitchboardDirectoryHeader(unittest.TestCase):

    def setUp(self):
        self.commandid = 125731893
        self.message = {
            'class': 'get_switchboard_directory_headers',
            'commandid': self.commandid,
        }

    def test_from_dict(self):
        msg = GetSwitchboardDirectoryHeaders.from_dict(self.message)

        self.assertEqual(msg.commandid, self.commandid)
