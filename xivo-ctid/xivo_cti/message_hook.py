# -*- coding: utf-8 -*-
# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

_hooks = []


def add_hook(conditions, function):
    _hooks.append((conditions, function))


def run_hooks(event):
    [func(event) for func in _get_matching_functions(event)]


def _get_matching_functions(event):
    result = []
    for conditions, function in _hooks:
        if _event_match_conditions(event, conditions):
            result.append(function)
    return result


def _event_match_conditions(event, conditions):
    for (name, value) in conditions:
        if name not in event or name in event and event[name] != value:
            return False
    return True
