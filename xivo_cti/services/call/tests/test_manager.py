# -*- coding: utf-8 -*-

# Copyright (C) 2014-2016 Avencall
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
from mock import Mock
from mock import sentinel
from xivo_cti.ami.ami_callback_handler import AMICallbackHandler
from xivo_cti.xivo_ami import AMIClass
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.services.call.manager import CallManager


class _BaseTest(unittest.TestCase):

    def setUp(self):
        self._ami = Mock(AMIClass)
        self._ami_cb_handler = Mock(AMICallbackHandler)
        self._connection = Mock(CTI)

        self.manager = CallManager(self._ami, self._ami_cb_handler)


class TestCallManager(_BaseTest):

    def test_answer_next_ringing_call(self):
        self.manager._get_answer_on_sip_ringing_fn = Mock(return_value=sentinel.fn)

        self.manager.answer_next_ringing_call(self._connection, sentinel.interface)

        self._ami_cb_handler.register_callback.assert_called_once_with(
            self.manager._answer_trigering_event, sentinel.fn)


class TestGetAnswerOnSIPRinging(_BaseTest):

    def test_that_ringing_on_the_good_hint_unregisters_the_callback(self):
        fn = self.manager._get_answer_on_sip_ringing_fn(self._connection, 'SIP/bcde')

        fn({
            'Peer': 'SIP/bcde',
        })

        self._ami_cb_handler.unregister_callback.assert_called_once_with(
            self.manager._answer_trigering_event, fn)
        self._connection.answer_cb.assert_called_once_with()

    def test_that_ringing_on_the_wrong_hint_unregisters_the_callback(self):
        fn = self.manager._get_answer_on_sip_ringing_fn(self._connection, 'SIP/bcde')

        fn({
            'Peer': 'SIP/bad',
        })

        self._assert_nothing_was_called()

    def _assert_nothing_was_called(self):
        assert_that(self._ami_cb_handler.unregister_callback.call_count, equal_to(0))
        assert_that(self._connection.answer_cb.call_count, equal_to(0))
