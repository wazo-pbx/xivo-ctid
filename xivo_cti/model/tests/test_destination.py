# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from xivo_cti.model.destination import Destination


class TestDestination(unittest.TestCase):

    def test_to_exten_no_error(self):
        d = Destination(1, 2, 3)
        d.to_exten()

    def test_equality(self):
        d1 = Destination('one', 'two', 'three')
        self.assertTrue(d1 == Destination('one', 'two', 'three'))
        self.assertFalse(d1 == Destination('one', 'two', None))
        self.assertFalse(d1 == Destination('one', None, 'three'))
        self.assertFalse(d1 == Destination(None, 'two', 'three'))
