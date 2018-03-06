# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo.caller_id import build_caller_id


class MeetmeDAO(object):

    def __init__(self, innerdata):
        self.innerdata = innerdata

    def get_caller_id_from_context_number(self, context, number):
        name = 'Conference'
        for meetme in self.innerdata.xod_config['meetmes'].keeplist.itervalues():
            if meetme['confno'] == number and meetme['context'] == context:
                name = 'Conference %s' % meetme['name']
                break
        return build_caller_id('', name, number)[0]
