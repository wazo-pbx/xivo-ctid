# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest
from mock import Mock
from hamcrest import assert_that, contains

from xivo_cti.dao.forward_dao import ForwardDAO

from xivo_dao.resources.func_key.model import Forward


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
        self.mock_forwards([Forward(user_id=self.user_id,
                                    type=fwd_type,
                                    number=expected_number),
                            Forward(user_id=self.user_id,
                                    type=fwd_type,
                                    number=None)])

        result = self.dao.unc_destinations(self.user_id)

        self.func_key_dao.find_all_forwards.assert_called_once_with(self.user_id,
                                                                    fwd_type)
        assert_that(result, contains(expected_number, ''))

    def test_rna_destinations(self):
        expected_number = '2345'
        fwd_type = 'noanswer'
        self.mock_forwards([Forward(user_id=self.user_id,
                                    type=fwd_type,
                                    number=expected_number),
                            Forward(user_id=self.user_id,
                                    type=fwd_type,
                                    number=None)])

        result = self.dao.rna_destinations(self.user_id)

        self.func_key_dao.find_all_forwards.assert_called_once_with(self.user_id,
                                                                    fwd_type)
        assert_that(result, contains(expected_number, ''))

    def test_busy_destinations(self):
        expected_number = '1234'
        fwd_type = 'busy'
        self.mock_forwards([Forward(user_id=self.user_id,
                                    type=fwd_type,
                                    number=expected_number),
                            Forward(user_id=self.user_id,
                                    type=fwd_type,
                                    number=None)])

        result = self.dao.busy_destinations(self.user_id)

        self.func_key_dao.find_all_forwards.assert_called_once_with(self.user_id,
                                                                    fwd_type)
        assert_that(result, contains(expected_number, ''))
