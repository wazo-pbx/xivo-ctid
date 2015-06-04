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
