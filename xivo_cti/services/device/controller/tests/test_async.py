# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock
from xivo_cti.services.device.controller.async import AsyncController


class TestAsyncController(unittest.TestCase):

    def setUp(self):
        self.device = Mock()
        self.answer_delay = 0.5
        self.timer_factory = Mock()
        self.controller = AsyncController(self.answer_delay, self.timer_factory)

    def test_answer_new_answered_not_implemented(self):
        self.assertRaises(NotImplementedError, self.controller.answer, self.device)

    def test_answer(self):
        # _new_answerer should usually be implemented in a subclass
        new_answerer = self.controller._new_answerer = Mock()

        self.controller.answer(self.device)

        new_answerer.assert_called_once_with(self.device)
        self.timer_factory.assert_called_once_with(self.answer_delay, new_answerer.return_value.answer)
        self.timer_factory.return_value.start.assert_called_once_with()
