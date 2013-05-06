# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from mock import sentinel
from mock import Mock
from hamcrest import *

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
