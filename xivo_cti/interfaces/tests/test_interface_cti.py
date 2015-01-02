# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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
from mock import patch
from mock import sentinel
from hamcrest import assert_that
from hamcrest import equal_to
from xivo_cti.ctiserver import CTIServer
from xivo_cti.interfaces.interface_cti import CTI
from xivo_cti.interfaces.interface_cti import NotLoggedException
from xivo_cti.services.device.manager import DeviceManager
from xivo_cti.cti.cti_message_encoder import CTIMessageDecoder,\
    CTIMessageEncoder


class TestCTI(unittest.TestCase):

    def setUp(self):
        self._ctiserver = Mock(CTIServer)
        self._cti_connection = CTI(self._ctiserver, CTIMessageDecoder(), CTIMessageEncoder())
        self._cti_connection.login_task = Mock()

    def test_user_id_not_connected(self):
        self.assertRaises(NotLoggedException, self._cti_connection.user_id)

    def test_user_id(self):
        user_id = 5
        self._cti_connection.connection_details['userid'] = user_id

        result = self._cti_connection.user_id()

        self.assertEqual(result, user_id)

    @patch('xivo_dao.user_dao.get_device_id')
    @patch('xivo_cti.ioc.context.context.get')
    def test_get_answer_cb(self, mock_device_manager_get, mock_get_device_id):
        mock_device_manager_get.return_value = mock_device_manager = Mock(DeviceManager)
        mock_device_manager.get_answer_fn.return_value = answer_fn = Mock()
        mock_get_device_id.return_value = device_id = 42

        self._cti_connection._get_answer_cb(5)()

        mock_device_manager.get_answer_fn.assert_called_once_with(device_id)
        answer_fn.assert_called_once_with()

    @patch('xivo_dao.user_dao.get_device_id', Mock(side_effect=LookupError))
    @patch('xivo_cti.ioc.context.context.get', Mock())
    def test_get_answer_cb_no_device(self):

        fn = self._cti_connection._get_answer_cb(5)

        assert_that(fn, equal_to(self._cti_connection.answer_cb))

    def test_attach_observer(self):
        callback = Mock()

        self._cti_connection.attach_observer(callback)
        self._cti_connection._notify_observers(sentinel)

        callback.assert_called_once_with(self._cti_connection, sentinel)

    def test_attach_same_observer_twice(self):
        callback = Mock()

        self._cti_connection.attach_observer(callback)
        self._cti_connection.attach_observer(callback)
        self._cti_connection._notify_observers(sentinel)

        callback.assert_called_once_with(self._cti_connection, sentinel)

    def test_detach_observer(self):
        callback = Mock()

        self._cti_connection.attach_observer(callback)
        self._cti_connection.detach_observer(callback)
        self._cti_connection._notify_observers(sentinel)

        self.assertFalse(callback.called)

    def test_detach_observer_doesnt_raise_on_unknown_observer(self):
        callback = Mock()

        self._cti_connection.detach_observer(callback)

    @patch('xivo_cti.ioc.context.context.get', Mock())
    def test_disconneted_notify_observers(self):
        callback = Mock()

        self._cti_connection.attach_observer(callback)
        self._cti_connection.disconnected(self._cti_connection.DisconnectCause.by_client)

        self.assertEqual(self._cti_connection.STATE_DISCONNECTED, self._cti_connection.state())
        callback.assert_called_once_with(self._cti_connection, self._cti_connection.STATE_DISCONNECTED)

    def test_notify_observer_raise_exception(self):
        callback1 = Mock(side_effect=Exception())
        callback2 = Mock()

        self._cti_connection.attach_observer(callback1)
        self._cti_connection.attach_observer(callback2)
        self._cti_connection._notify_observers(sentinel)

        callback1.assert_called_once_with(self._cti_connection, sentinel)
        callback2.assert_called_once_with(self._cti_connection, sentinel)
