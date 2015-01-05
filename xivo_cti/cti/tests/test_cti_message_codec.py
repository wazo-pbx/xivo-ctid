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
