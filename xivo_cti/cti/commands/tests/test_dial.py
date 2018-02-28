# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.cti.commands.dial import Dial
from hamcrest import assert_that
from hamcrest import equal_to


class TestDial(unittest.TestCase):

    def setUp(self):
        self._commandid = 125708937534
        self.dial_message = {
            'class': 'ipbxcommand',
            'command': 'dial',
            'commandid': self._commandid,
        }

    def test_from_dict_url_style_destination(self):
        dest = 'voicemail:xivo/123'
        self.dial_message['destination'] = dest

        dial = Dial.from_dict(self.dial_message)

        assert_that(dial.commandid, equal_to(self._commandid), 'Command ID')
        assert_that(dial.destination, equal_to(dest), 'Dialed destination')

    def test_from_dict_other_destination(self):
        dest = '1234'
        self.dial_message['destination'] = dest
        dial = Dial.from_dict(self.dial_message)

        assert_that(dial.commandid, equal_to(self._commandid), 'Command ID')
        assert_that(dial.destination, equal_to(dest), 'Dialed extension')
