# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti import config


class InnerdataDAO(object):

    def __init__(self, innerdata):
        self.innerdata = innerdata

    def get_presences(self, profile):
        profile_id = config['profiles'].get(profile).get('userstatus')
        return config['userstatus'].get(profile_id).keys()
