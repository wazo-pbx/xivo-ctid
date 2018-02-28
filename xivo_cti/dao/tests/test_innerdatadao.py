# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import assert_that
from hamcrest import contains_inanyorder
from mock import Mock
from mock import patch
from xivo_cti.dao.innerdata_dao import InnerdataDAO
from xivo_cti.innerdata import Safe


class TestInnerdataDAO(unittest.TestCase):

    def setUp(self):
        self.innerdata = Mock(Safe)
        self.innerdata_dao = InnerdataDAO(self.innerdata)

    @patch('xivo_cti.dao.innerdata_dao.config', {'profiles': {'client': {'userstatus': 2}},
                                                 'userstatus': {
                                                     2: {'available': {},
                                                         'disconnected': {}}}})
    def test_get_presences(self):
        profile = 'client'
        expected_result = ['available', 'disconnected']

        result = self.innerdata_dao.get_presences(profile)

        assert_that(result, contains_inanyorder(*expected_result))
