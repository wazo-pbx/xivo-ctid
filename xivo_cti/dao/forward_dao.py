# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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
