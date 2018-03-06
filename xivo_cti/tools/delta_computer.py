# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
                       if new_key in old_dict and
                       old_dict[new_key] != new_dict[new_key])
        return DictDelta(added_items, changed, removed_items)

    @classmethod
    def compute_delta_no_delete(cls, new_dict, old_dict):
        delta_delete = cls.compute_delta(new_dict, old_dict)
        delta_no_delete = DictDelta(delta_delete.add, delta_delete.change, {})
        return delta_no_delete
