# -*- coding: utf-8 -*-

# XiVO CTI Server
# Copyright (C) 2009-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import namedtuple

DictDelta = namedtuple('DictDelta', ['add', 'change', 'delete'])


class DeltaComputer(object):

    @staticmethod
    def compute_delta(new_dict, old_dict):
        added_keys = set(new_dict).difference(old_dict)
        added_items = dict((item_key, new_dict[item_key]) for item_key in added_keys)
        removed_keys = set(old_dict).difference(new_dict)
        removed_items = dict((item_key, old_dict[item_key]) for item_key in removed_keys)
        changed = dict((new_key, new_value) for (new_key, new_value) in new_dict.iteritems()
                       if new_key in old_dict
                       and old_dict[new_key] != new_dict[new_key])
        return DictDelta(added_items, changed, removed_items)

    @classmethod
    def compute_delta_no_delete(cls, new_dict, old_dict):
        delta_delete = cls.compute_delta(new_dict, old_dict)
        delta_no_delete = DictDelta(delta_delete.add, delta_delete.change, {})
        return delta_no_delete
