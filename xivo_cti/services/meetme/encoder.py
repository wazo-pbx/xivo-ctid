# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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


def encode_room_number_pairs(pairs):
    list = [{'room_number': room_number,
             'user_number': user_number}
            for room_number, user_number in pairs]

    return {'class': 'meetme_user',
            'list': sorted(list)}
