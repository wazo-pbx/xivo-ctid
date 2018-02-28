# -*- coding: utf-8 -*-
# Copyright (C) 2009-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti import dao


class PresenceServiceManager(object):

    def __init__(self):
        self.dao = dao

    def is_valid_presence(self, profile, presence):
        presences = self.dao.innerdata.get_presences(profile)
        return presence in presences
