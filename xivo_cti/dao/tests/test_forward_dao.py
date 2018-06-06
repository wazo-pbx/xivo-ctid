# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock
from hamcrest import assert_that, contains

from xivo_cti.dao.forward_dao import ForwardDAO

from xivo_dao.alchemy.func_key_dest_forward import FuncKeyDestForward as Forward


class TestForwardDAO(unittest.TestCase):

    def setUp(self):
        self.func_key_dao = Mock()
        self.dao = ForwardDAO(self.func_key_dao)
        self.user_id = 1

    def mock_forwards(self, forwards):
        self.func_key_dao.find_all_forwards.return_value = forwards

    def test_unc_destinations(self):
        expected_number = '1234'
        fwd_type = 'unconditional'
        self.mock_forwards([Forward(forward=fwd_type,
                                    number=expected_number),
                            Forward(forward=fwd_type,
                                    number=None)])

        result = self.dao.unc_destinations(self.user_id)

        self.func_key_dao.find_all_forwards.assert_called_once_with(self.user_id,
                                                                    fwd_type)
        assert_that(result, contains(expected_number, ''))

    def test_rna_destinations(self):
        expected_number = '2345'
        fwd_type = 'noanswer'
        self.mock_forwards([Forward(forward=fwd_type,
                                    number=expected_number),
                            Forward(forward=fwd_type,
                                    number=None)])

        result = self.dao.rna_destinations(self.user_id)

        self.func_key_dao.find_all_forwards.assert_called_once_with(self.user_id,
                                                                    fwd_type)
        assert_that(result, contains(expected_number, ''))

    def test_busy_destinations(self):
        expected_number = '1234'
        fwd_type = 'busy'
        self.mock_forwards([Forward(forward=fwd_type,
                                    number=expected_number),
                            Forward(forward=fwd_type,
                                    number=None)])

        result = self.dao.busy_destinations(self.user_id)

        self.func_key_dao.find_all_forwards.assert_called_once_with(self.user_id,
                                                                    fwd_type)
        assert_that(result, contains(expected_number, ''))
