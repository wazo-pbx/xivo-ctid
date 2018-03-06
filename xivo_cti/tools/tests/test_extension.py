# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.tools.extension import normalize_exten
from xivo_cti.tools.extension import InvalidExtension


class TestInvalidExtension(unittest.TestCase):
    def test_exten_attribute(self):
        self.assertEqual(InvalidExtension('1234').exten, '1234')


class TestExtension(unittest.TestCase):

    def test_normalize_exten(self):
        extens = ['00.11.22.33.44',
                  '00 11 22 33 44',
                  '00-_11@%^& 22":<>/33?:";44']
        for exten in extens:
            self.assertEqual(normalize_exten(exten), '0011223344')

    def test_normalize_exten_with_plus(self):
        extens = ['+00.11.22.33.44',
                  '+00 11 22 33 44',
                  '+00-_11@%^& 22":<>/33?:";44']
        for exten in extens:
            self.assertEqual(normalize_exten(exten), '+0011223344')

    def test_normalize_exten_any_valid_char(self):
        exten = '-@%^& ":<>/?:";'
        self.assertRaises(InvalidExtension, normalize_exten, exten)

    def test_normalize_exten_caller_id(self):
        exten = '"User 1" <1001>"'
        self.assertEqual(normalize_exten(exten), '1001')
