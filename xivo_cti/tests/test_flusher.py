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

import unittest

from mock import Mock
from xivo_cti.flusher import Flusher


class TestFlusher(unittest.TestCase):

    def setUp(self):
        self.flusher = Flusher()
        self.flushable = Mock()

    def test_add(self):
        self.flusher.add(self.flushable)

        self.assertFalse(self.flushable.flush.called)

    def test_flush(self):
        self.flusher.add(self.flushable)
        self.flusher.flush()

        self.flushable.flush.assert_called_once_with()

    def test_flush_queue_is_empty_after_flush(self):
        self.flusher.add(self.flushable)
        self.flusher.flush()
        self.flusher.flush()

        self.flushable.flush.assert_called_once_with()
