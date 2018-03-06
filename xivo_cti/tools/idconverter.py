# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+


class IdConverter(object):

    @staticmethod
    def xid_to_id(identifier):
        if identifier:
            identifier = str(identifier)
            id_split_list = identifier.split('/')
            return id_split_list[-1]
