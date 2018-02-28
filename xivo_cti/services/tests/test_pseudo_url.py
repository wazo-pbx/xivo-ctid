# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import assert_that
from hamcrest import equal_to

from xivo_cti.model.destination import Destination
from xivo_cti.services.pseudo_url import PseudoURL


class TestPseudoURL(unittest.TestCase):

    def setUp(self):
        self._ipbxid = 'xivo'

    def test_parse_url_exten(self):
        exten = '1234'
        exten_url = 'exten:{0}/{1}'.format(self._ipbxid, exten)

        expected = Destination('exten', self._ipbxid, exten)

        assert_that(PseudoURL.parse(exten_url), equal_to(expected), 'Parsed exten URL')

    def test_parse_url_invalid(self):
        self.assertRaises(ValueError, PseudoURL.parse, '1234')
