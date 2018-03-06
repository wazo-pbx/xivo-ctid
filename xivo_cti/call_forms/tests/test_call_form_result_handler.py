# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import assert_that
from hamcrest import equal_to
from mock import Mock

from ..call_form_result_handler import CallFormResultHandler, CallFormResultEvent


class TestCallFormResultHandler(unittest.TestCase):

    def setUp(self):
        self._bus_publisher = Mock()
        self._handler = CallFormResultHandler(self._bus_publisher)

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

    def test_send_call_form_result(self):
        variables = {'foo': 'bar'}
        expected_event = CallFormResultEvent(42, variables)

        self._handler._send_call_form_result(42, variables)

        self._bus_publisher.publish.assert_called_once_with(expected_event)
