# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

import copy


def encode_update(config):
    tmp = copy.deepcopy(config)

    for conf_number, conf_config in config.iteritems():
        tmp[conf_number]['member_count'] = len(config[conf_number]['members'])
        tmp[conf_number].pop('context')
        tmp[conf_number]['members'] = {}
        for user_number, user_config in config[conf_number]['members'].iteritems():
            tmp[conf_number]['members'][str(user_number)] = copy.deepcopy(user_config)
            tmp[conf_number]['members'][str(user_number)].pop('channel', None)
    tmp = _swap_bool_to_yes_no(tmp)

    return {'class': 'meetme_update',
            'config': tmp}


def encode_update_for_contexts(config, contexts):
    tmp = copy.deepcopy(config)

    for conf_number, conf_config in config.iteritems():
        if config[conf_number]['context'] not in contexts:
            tmp.pop(conf_number)

    return encode_update(tmp)


def encode_user(conf_number, usernum):
    return {'class': 'meetme_user',
            'meetme': conf_number,
            'usernum': usernum}


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


def encode_room_number_pairs(pairs):
    list = [{'room_number': room_number,
             'user_number': user_number}
             for room_number, user_number in pairs]

    return {'class': 'meetme_user',
            'list': sorted(list)}
