# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

from collections import namedtuple
from collections import defaultdict


CallFormVariable = namedtuple('CallFormVariable', ['type', 'name', 'value'])


class VariableAggregator(object):

    def __init__(self):
        self._vars = defaultdict(lambda: defaultdict(dict))

    def clean(self, uid):
        if uid in self._vars:
            del self._vars[uid]

    def get(self, uid):
        return self._vars[uid]

    def set(self, uid, var):
        self._vars[uid][var.type][var.name] = var.value
