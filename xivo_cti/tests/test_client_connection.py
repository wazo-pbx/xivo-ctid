# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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
