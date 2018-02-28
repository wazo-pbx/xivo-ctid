# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
