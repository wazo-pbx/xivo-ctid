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


class UserFeaturesDAO(object):

    def __init__(self):
        pass

    def enable_dnd(self, user_id):
        userfeatures_dao.enable_dnd(user_id)
        self._innerdata.xod_config['users'].keeplist[user_id]['enablednd'] = True

    def disable_dnd(self, user_id):
        userfeatures_dao.disable_dnd(user_id)
        self._innerdata.xod_config['users'].keeplist[user_id]['enablednd'] = False

    def enable_filter(self, user_id):
        userfeatures_dao.enable_filter(user_id)
        self._innerdata.xod_config['users'].keeplist[user_id]['incallfilter'] = True

    def disable_filter(self, user_id):
        userfeatures_dao.disable_filter(user_id)
        self._innerdata.xod_config['users'].keeplist[user_id]['incallfilter'] = False

    def enable_unconditional_fwd(self, user_id, destination):
        userfeatures_dao.enable_unconditional_fwd(user_id, destination)
        self._innerdata.xod_config['users'].keeplist[user_id]['enableunc'] = True
        self._innerdata.xod_config['users'].keeplist[user_id]['destunc'] = destination

    def disable_unconditional_fwd(self, user_id, destination):
        userfeatures_dao.disable_unconditional_fwd(user_id, destination)
        self._innerdata.xod_config['users'].keeplist[user_id]['destunc'] = destination
        self._innerdata.xod_config['users'].keeplist[user_id]['enableunc'] = False

    def enable_rna_fwd(self, user_id, destination):
        userfeatures_dao.enable_rna_fwd(user_id, destination)
        self._innerdata.xod_config['users'].keeplist[user_id]['enablerna'] = True
        self._innerdata.xod_config['users'].keeplist[user_id]['destrna'] = destination

    def disable_rna_fwd(self, user_id, destination):
        userfeatures_dao.disable_rna_fwd(user_id, destination)
        self._innerdata.xod_config['users'].keeplist[user_id]['destrna'] = destination
        self._innerdata.xod_config['users'].keeplist[user_id]['enablerna'] = False

    def enable_busy_fwd(self, user_id, destination):
        userfeatures_dao.enable_busy_fwd(user_id, destination)
        self._innerdata.xod_config['users'].keeplist[user_id]['enablebusy'] = True
        self._innerdata.xod_config['users'].keeplist[user_id]['destbusy'] = destination

    def disable_busy_fwd(self, user_id, destination):
        userfeatures_dao.disable_busy_fwd(user_id, destination)
        self._innerdata.xod_config['users'].keeplist[user_id]['destbusy'] = destination
        self._innerdata.xod_config['users'].keeplist[user_id]['enablebusy'] = False

    def disconnect(self, user_id):
        userdata = self._innerdata.xod_status['users'][user_id]
        userdata['connection'] = None
        userdata['last-logouttimestamp'] = time.time()

    def set_presence(self, user_id, presence):
        userdata = self._innerdata.xod_status['users'][user_id]
        userdata['availstate'] = presence
