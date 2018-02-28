# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from collections import deque


class Flusher(object):

    def __init__(self):
        self._queue = deque()

    def add(self, flushable):
        self._queue.append(flushable)

    def flush(self):
        for flushable in self._queue:
            flushable.flush()
        self._queue.clear()
