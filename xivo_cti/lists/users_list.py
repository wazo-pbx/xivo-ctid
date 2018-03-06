# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti_anylist import ContextAwareAnyList


class UsersList(ContextAwareAnyList):

    def __init__(self, innerdata):
        self._innerdata = innerdata
        ContextAwareAnyList.__init__(self, 'users')

    def get_contexts(self, user_id):
        try:
            user = self.keeplist[user_id]
        except KeyError:
            return []
        else:
            user_context = user['context']
            if user_context is None:
                return []
            else:
                return [user_context]
