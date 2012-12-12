#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2012  Avencall
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

import logging
import time

from xivo_dao import userfeatures_dao

logger = logging.getLogger("UserFeaturesDAO")


class UserDAO(object):

    def __init__(self, innerdata):
        self.innerdata = innerdata

    def _phone(self, phone_id):
        return self.innerdata.xod_config['phones'].keeplist[phone_id]

    def _user(self, user_id):
        return self.innerdata.xod_config['users'].keeplist[user_id]

    def _user_status(self, user_id):
        return self.innerdata.xod_status['users'][user_id]

    def enable_dnd(self, user_id):
        userfeatures_dao.enable_dnd(user_id)
        user = self._user(user_id)
        user['enablednd'] = True

    def disable_dnd(self, user_id):
        userfeatures_dao.disable_dnd(user_id)
        user = self._user(user_id)
        user['enablednd'] = False

    def enable_filter(self, user_id):
        userfeatures_dao.enable_filter(user_id)
        user = self._user(user_id)
        user['incallfilter'] = True

    def disable_filter(self, user_id):
        userfeatures_dao.disable_filter(user_id)
        user = self._user(user_id)
        user['incallfilter'] = False

    def enable_unconditional_fwd(self, user_id, destination):
        userfeatures_dao.enable_unconditional_fwd(user_id, destination)
        user = self._user(user_id)
        user['enableunc'] = True
        user['destunc'] = destination

    def disable_unconditional_fwd(self, user_id, destination):
        userfeatures_dao.disable_unconditional_fwd(user_id, destination)
        user = self._user(user_id)
        user['destunc'] = destination
        user['enableunc'] = False

    def enable_rna_fwd(self, user_id, destination):
        userfeatures_dao.enable_rna_fwd(user_id, destination)
        user = self._user(user_id)
        user['enablerna'] = True
        user['destrna'] = destination

    def disable_rna_fwd(self, user_id, destination):
        userfeatures_dao.disable_rna_fwd(user_id, destination)
        user = self._user(user_id)
        user['destrna'] = destination
        user['enablerna'] = False

    def enable_busy_fwd(self, user_id, destination):
        userfeatures_dao.enable_busy_fwd(user_id, destination)
        user = self._user(user_id)
        user['enablebusy'] = True
        user['destbusy'] = destination

    def disable_busy_fwd(self, user_id, destination):
        userfeatures_dao.disable_busy_fwd(user_id, destination)
        user = self._user(user_id)
        user['destbusy'] = destination
        user['enablebusy'] = False

    def disconnect(self, user_id):
        user_status = self._user_status(user_id)
        user_status['connection'] = None
        user_status['last-logouttimestamp'] = time.time()

    def set_presence(self, user_id, presence):
        user_status = self._user_status(user_id)
        user_status['availstate'] = presence

    def get_line_identity(self, user_id):
        user = self._user(user_id)
        line = self._phone(user['linelist'].pop())

        return line['identity']

    def get_context(self, user_id):
        user = self._user(user_id)
        line = self._phone(user['linelist'].pop())

        return line['context']
