# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_utils import session_scope


class ForwardDAO(object):

    def __init__(self, dao):
        self.dao = dao

    def unc_destinations(self, user_id):
        return self._filter_fwd_type(user_id, 'unconditional')

    def rna_destinations(self, user_id):
        return self._filter_fwd_type(user_id, 'noanswer')

    def busy_destinations(self, user_id):
        return self._filter_fwd_type(user_id, 'busy')

    def _filter_fwd_type(self, user_id, fwd_type):
        with session_scope():
            return [fwd.number or ''
                    for fwd in self.dao.find_all_forwards(user_id, fwd_type)]
