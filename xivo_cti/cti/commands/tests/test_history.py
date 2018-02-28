# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.cti.commands.history import History


class TestHistory(unittest.TestCase):

    def test_from_dict(self):
        message = self._build_message(size='10')

        history = History.from_dict(message)

        self.assertEqual(history.size, 10)

    def _build_message(self, size):
        return {
            'class': 'ipbxcommand',
            'command': 'history',
            'size': size,
        }
