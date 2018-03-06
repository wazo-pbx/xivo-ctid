# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import sentinel
from mock import Mock
from hamcrest import assert_that
from hamcrest import equal_to

from xivo_cti.ami.ami_response_handler import AMIResponseHandler


class TestAMIResponseHandler(unittest.TestCase):

    def setUp(self):
        self.handler = AMIResponseHandler.get_instance()

    def test_register_callback(self):
        action_id = sentinel
        cb = sentinel

        self.handler.register_callback(action_id, cb)

        assert_that(self.handler._callbacks[action_id], equal_to(cb), 'Registered callback')

    def test_handle_response(self):
        action_id_1, cb_1 = 'one', Mock()
        action_id_2, cb_2 = 'two', Mock(side_effect=AssertionError('Second callback should not be called'))
        response = {
            'Response': 'Success',
            'ActionID': action_id_1,
            'Message': 'Originate successfully queued',
        }

        self.handler.register_callback(action_id_1, cb_1)
        self.handler.register_callback(action_id_2, cb_2)

        self.handler.handle_response(response)

        cb_1.assert_called_once_with(response)

        assert_that(action_id_1 in self.handler._callbacks, equal_to(False), 'Key is removed from dict')

    def test_handle_response_no_action_id_no_error(self):
        self.handler.handle_response({
            'Response': 'Success',
            'Message': 'Originate successfully queued',
        })
