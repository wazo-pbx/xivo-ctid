# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
