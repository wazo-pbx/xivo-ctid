# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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

from hamcrest import assert_that
from hamcrest import equal_to
from mock import Mock, patch, sentinel

from xivo_bus import Marshaler

from ..call_form_result_handler import CallFormResultHandler, CallFormResultEvent


class TestCallFormResultHandler(unittest.TestCase):

    def setUp(self):
        self._marshaler = Marshaler('my-uuid')
        self._bus_publish = Mock()
        self._handler = CallFormResultHandler(self._bus_publish, self._marshaler)

    def test_parse(self):
        user_id = 42
        variables = {
            'XIVOFORM_firstname': 'Robert',
            'XIVOFORM_lastname': 'Lepage',
        }
        cleaned_up_variables = {
            'firstname': 'Robert',
            'lastname': 'Lepage',
        }
        self._handler._send_call_form_result = Mock()
        self._handler.parse(user_id, variables)

        self._handler._send_call_form_result.assert_called_once_with(
            user_id,
            cleaned_up_variables,
        )

    def test_malformed_variable(self):
        variables = {
            'firstname': 'Robert',
            'XIVOFORM_lastname': 'Lepage',
            'XIVOFORM_': 'invalid',
            'XIVOFORM_client_number': '1234',
        }
        expected_variables = {
            'lastname': 'Lepage',
            'client_number': '1234',
        }

        assert_that(self._handler._clean_variables(variables),
                    equal_to(expected_variables))

    @patch('xivo_cti.call_forms.call_form_result_handler.config',
           {'bus': {'routing_keys': {'call_form_result': sentinel.routing_key}}})
    def test_send_call_form_result(self):
        variables = {'foo': 'bar'}
        expected_msg = self._marshaler.marshal_message(
            CallFormResultEvent(42, variables))

        self._handler._send_call_form_result(42, variables)

        self._bus_publish.assert_called_once_with(expected_msg,
                                                  routing_key=sentinel.routing_key)
