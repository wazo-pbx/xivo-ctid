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

import copy


def encode(config):
    tmp = copy.deepcopy(config)

    for conf_number, conf_config in config.iteritems():
        tmp[conf_number]['member_count'] = len(config[conf_number]['members'])
        for user_number, user_config in tmp[conf_number]['members'].iteritems():
            tmp[conf_number]['members'][user_number].pop('channel')
    tmp = _swap_bool_to_yes_no(tmp)

    return tmp


def _swap_bool_to_yes_no(d):
    for name, value in d.iteritems():
        if not isinstance(value, dict):
            if value is True:
                d[name] = 'Yes'
            elif value is False:
                d[name] = 'No'
        else:
            _swap_bool_to_yes_no(value)
    return d
