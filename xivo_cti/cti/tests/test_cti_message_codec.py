# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import json
import mock
import unittest

from xivo_cti.cti.cti_message_codec import CTIMessageDecoder, CTIMessageEncoder, \
    CTIMessageCodec


class TestCTIMessageCodec(unittest.TestCase):

    def setUp(self):
        self.cti_msg_codec = CTIMessageCodec()

    def test_new_decoder(self):
        decoder = self.cti_msg_codec.new_decoder()

        self.assertIsInstance(decoder, CTIMessageDecoder)

    def test_new_encoder(self):
        encoder = self.cti_msg_codec.new_encoder()

        self.assertIsInstance(encoder, CTIMessageEncoder)


class TestCTIMessageDecoder(unittest.TestCase):

    def setUp(self):
        self.cti_msg_decoder = CTIMessageDecoder()

    def test_decode_one_msg(self):
        data = '{"class": "foo"}\n'
        expected_msgs = [{'class': 'foo'}]

        msgs = self.cti_msg_decoder.decode(data)

        self.assertEqual(expected_msgs, msgs)

    def test_decode_less_than_one_msg(self):
        data = '{"class": "foo"}\n'
        data1 = data[:len(data) / 2]
        data2 = data[len(data) / 2:]
        expected_msgs = [{'class': 'foo'}]

        msgs = self.cti_msg_decoder.decode(data1)

        self.assertEqual([], msgs)

        msgs = self.cti_msg_decoder.decode(data2)

        self.assertEqual(expected_msgs, msgs)

    def test_decode_more_than_one_msg(self):
        data = '{"class": "foo1"}\n{"class": "foo2"}\n'
        expected_msgs = [{'class': 'foo1'}, {'class': 'foo2'}]

        msgs = self.cti_msg_decoder.decode(data)

        self.assertEqual(expected_msgs, msgs)


class TestCTIMessageEncoder(unittest.TestCase):

    def setUp(self):
        self.time = 123
        self.cti_msg_encoder = CTIMessageEncoder()

    @mock.patch('time.time')
    def test_encode(self, mock_time):
        mock_time.return_value = self.time
        msg = {'class': 'foo'}
        expected_msg = {'class': 'foo', 'timenow': self.time}

        encoded_msg = self.cti_msg_encoder.encode(msg)

        self.assertTrue(encoded_msg.endswith('\n'))
        self.assertEqual(expected_msg, json.loads(encoded_msg[:-1]))
