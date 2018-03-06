# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from collections import namedtuple
from collections import defaultdict


CallFormVariable = namedtuple('CallFormVariable', ['type', 'name', 'value'])


class VariableAggregator(object):

    def __init__(self):
        self._vars = defaultdict(lambda: defaultdict(dict))
        self._refcount = defaultdict(lambda: 1)

    def get(self, uid):
        return self._vars[uid]

    def set(self, uid, var):
        self._vars[uid][var.type][var.name] = var.value

    def on_agent_connect(self, uid):
        self._refcount[uid] += 1

    def on_agent_complete(self, uid):
        self._decrease_refcount(uid)

    def on_hangup(self, uid):
        self._decrease_refcount(uid)

    def _decrease_refcount(self, uid):
        self._refcount[uid] -= 1
        if self._refcount[uid] == 0:
            del self._refcount[uid]
            self._vars.pop(uid, None)
