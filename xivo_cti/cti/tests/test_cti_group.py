# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import mock
import unittest

from xivo_cti.client_connection import ClientConnection
from xivo_cti.cti.cti_group import CTIGroup, CTIGroupFactory
from xivo_cti.cti.cti_message_codec import CTIMessageEncoder, CTIMessageCodec
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

    def test_add_and_send_message(self):
        self.cti_group.add(self.interface_cti)
        self.cti_group.send_message(self.msg)
        self.cti_group.flush()

        self.cti_msg_encoder.encode.assert_called_once_with(self.msg)
        self.interface_cti.send_encoded_message.assert_called_once_with(self.encoded_msg)

    def test_add_same_interface_twice(self):
        self.cti_group.add(self.interface_cti)
        self.cti_group.add(self.interface_cti)
        self.cti_group.send_message(self.msg)
        self.cti_group.flush()

        self.interface_cti.send_encoded_message.assert_called_once_with(self.encoded_msg)

    def test_remove(self):
        self.cti_group.add(self.interface_cti)
        self.cti_group.remove(self.interface_cti)
        self.cti_group.send_message(self.msg)

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
