# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

import mock
import unittest

from xivo_cti.client_connection import ClientConnection
from xivo_cti.cti.cti_group import CTIGroup, CTIGroupFactory
from xivo_cti.cti.cti_message_encoder import CTIMessageEncoder, CTIMessageCodec
from xivo_cti.flusher import Flusher
from xivo_cti.interfaces.interface_cti import CTI


class TestCTIGroup(unittest.TestCase):

    def setUp(self):
        self.msg = {'class': 'test'}
        self.encoded_msg = '{"class": "test"}\n'
        self.cti_msg_encoder = mock.Mock(CTIMessageEncoder)
        self.cti_msg_encoder.encode.return_value = self.encoded_msg
        self.flusher = mock.Mock(Flusher)
        self.cti_group = CTIGroup(self.cti_msg_encoder, self.flusher)
        self.interface_cti = mock.Mock(CTI)
        self.interface_cti.STATE_NEW = CTI.STATE_NEW
        self.interface_cti.STATE_DISCONNECTED = CTI.STATE_DISCONNECTED
        self.interface_cti.state.return_value = CTI.STATE_NEW

    def test_add_and_send_message(self):
        self.cti_group.add(self.interface_cti)
        self.cti_group.send_message(self.msg)
        self.cti_group.flush()

        self.cti_msg_encoder.encode.assert_called_once_with(self.msg)
        self.interface_cti.attach_observer.assert_called_once_with(self.cti_group._on_interface_cti_update)
        self.interface_cti.send_encoded_message.assert_called_once_with(self.encoded_msg)

    def test_add_same_interface_twice(self):
        self.cti_group.add(self.interface_cti)
        self.cti_group.add(self.interface_cti)
        self.cti_group.send_message(self.msg)
        self.cti_group.flush()

        self.interface_cti.send_encoded_message.assert_called_once_with(self.encoded_msg)

    def test_add_interface_in_state_disconnected(self):
        self.interface_cti.state.return_value = CTI.STATE_DISCONNECTED

        self.cti_group.add(self.interface_cti)
        self.cti_group.send_message(self.msg)

        self.assertFalse(self.interface_cti.send_encoded_message.called)

    def test_on_interface_cti_update(self):
        self.cti_group.add(self.interface_cti)
        self.cti_group._on_interface_cti_update(self.interface_cti, self.interface_cti.STATE_DISCONNECTED)
        self.cti_group.send_message(self.msg)

        self.assertFalse(self.interface_cti.send_encoded_message.called)

    def test_remove(self):
        self.cti_group.add(self.interface_cti)
        self.cti_group.remove(self.interface_cti)
        self.cti_group.send_message(self.msg)

        self.interface_cti.detach_observer.assert_called_once_with(self.cti_group._on_interface_cti_update)
        self.assertFalse(self.interface_cti.send_encoded_message.called)

    def test_remove_doesnt_raise_on_unknown_interface(self):
        self.cti_group.remove(self.interface_cti)

    def test_send_message_calls_flusher_add_only_once(self):
        self.cti_group.send_message(self.msg)
        self.cti_group.send_message(self.msg)

        self.flusher.add.assert_called_once_with(self.cti_group)

    def test_send_message_and_flush_twice(self):
        self.cti_group.add(self.interface_cti)

        self.cti_group.send_message(self.msg)
        self.cti_group.flush()

        self.interface_cti.send_encoded_message.assert_called_once_with(self.encoded_msg)
        self.interface_cti.send_encoded_message.reset_mock()

        self.cti_group.send_message(self.msg)
        self.cti_group.flush()

        self.interface_cti.send_encoded_message.assert_called_once_with(self.encoded_msg)

    def test_send_message_and_flush_two_interfaces_and_two_messages(self):
        interface_cti1 = mock.Mock(CTI)
        interface_cti2 = mock.Mock(CTI)

        self.cti_group.add(interface_cti1)
        self.cti_group.add(interface_cti2)
        self.cti_group.send_message(self.msg)
        self.cti_group.send_message(self.msg)
        self.cti_group.flush()

        encoded_msg = self.encoded_msg * 2
        interface_cti1.send_encoded_message.assert_called_once_with(encoded_msg)
        interface_cti2.send_encoded_message.assert_called_once_with(encoded_msg)

    def test_send_message_and_flush_when_interface_cti_exception(self):
        interface_cti1 = mock.Mock(CTI)
        interface_cti1.send_encoded_message.side_effect = ClientConnection.CloseException()
        interface_cti2 = mock.Mock(CTI)

        self.cti_group.add(interface_cti1)
        self.cti_group.add(interface_cti2)
        self.cti_group.send_message(self.msg)
        self.cti_group.flush()

        interface_cti1.send_encoded_message.assert_called_once_with(self.encoded_msg)
        interface_cti2.send_encoded_message.assert_called_once_with(self.encoded_msg)
        self.assertNotIn(interface_cti1, self.cti_group._interfaces)


class TestCTIGroupFactory(unittest.TestCase):

    def setUp(self):
        self.cti_msg_codec = mock.Mock(CTIMessageCodec)
        self.flusher = mock.Mock()
        self.cti_group_factory = CTIGroupFactory(self.cti_msg_codec, self.flusher)

    def test_new_cti_group(self):
        cti_group = self.cti_group_factory.new_cti_group()

        self.cti_msg_codec.new_encoder.assert_called_once_with()
        self.assertIsInstance(cti_group, CTIGroup)
