# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock
from xivo_cti.client_connection import ClientConnection


class TestClientConnection(unittest.TestCase):

    def setUp(self):
        self.socket = Mock()
        self.client_conn = ClientConnection(self.socket)

    def test_process_sending_returns_when_n_is_zero(self):
        # This case happens when:
        # - self.socket is a SSLSocket object,
        # - the underlying TCP socket is full or nearly full (i.e. it's not
        #   possible to write the next TLS record completely)
        self.socket.send.return_value = 0
        self.client_conn.append_queue('foo')

        self.client_conn.process_sending()

        self.socket.send.assert_called_once_with('foo')
        self.assertEqual(self.client_conn.sendqueue.popleft(), 'foo')
