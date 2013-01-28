# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

_hooks = []


def add_hook(conditions, function):
    _hooks.append((conditions, function))


def run_hooks(event):
    for func in _get_matching_functions(event):
        func(event)


def _get_matching_functions(event):
    for conditions, function in _hooks:
        if _event_match_conditions(event, conditions):
            yield function


def _event_match_conditions(event, conditions):
    for name, value in conditions:
        if name not in event or event[name] != value:
            return False
    return True
