# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from xivo_cti.tools.idconverter import IdConverter


class TestIdConverter(unittest.TestCase):

    def test_xid_to_id_input_empty(self):
        identifier = ''
        expected_result = None

        result = IdConverter.xid_to_id(identifier)

        self.assertEqual(result, expected_result)

    def test_xid_to_id_input_int(self):
        identifier = 12
        expected_result = '12'

        result = IdConverter.xid_to_id(identifier)

        self.assertEqual(result, expected_result)

    def test_xid_to_id_input_id(self):
        identifier = '12'
        expected_result = '12'

        result = IdConverter.xid_to_id(identifier)

        self.assertEqual(result, expected_result)

    def test_xid_to_id_input_xid(self):
        identifier = 'ipbxid/12'
        expected_result = '12'

        result = IdConverter.xid_to_id(identifier)

        self.assertEqual(result, expected_result)

    def test_xid_to_id_None(self):
        identifier = None
        expected_result = None

        result = IdConverter.xid_to_id(identifier)

        self.assertEqual(result, expected_result)
