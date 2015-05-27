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

import threading


class AsyncController(object):

    def __init__(self, answer_delay, timer_factory=threading.Timer):
        self._answer_delay = answer_delay
        self._timer_factory = timer_factory

    def answer(self, device):
        answerer = self._new_answerer(device)
        timer = self._timer_factory(self._answer_delay, answerer.answer)
        timer.start()

    def _new_answerer(self, device):
        raise NotImplementedError()
