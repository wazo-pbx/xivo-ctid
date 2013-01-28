# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

import logging

from xivo_cti.cti_anylist import AnyList

logger = logging.getLogger('userlist')


class UsersList(AnyList):

    def __init__(self, innerdata):
        self._innerdata = innerdata
        AnyList.__init__(self, 'users')

    def finduser(self, userid):
        for userinfo in self.keeplist.itervalues():
            if userinfo and userinfo.get('enableclient') and userinfo.get('loginclient') == userid:
                return userinfo

    def users(self):
        return self.keeplist

    def connected_users(self):
        lst = {}
        for username, userinfo in self.keeplist.iteritems():
            if 'login' in userinfo:
                lst[username] = userinfo
        return lst

    def get_contexts(self, user_id):
        return self._innerdata.xod_config['phones'].get_contexts_for_user(user_id)

    def list_ids_in_contexts(self, contexts):
        phonelist = self._innerdata.xod_config['phones']
        return phonelist.list_user_ids_in_contexts(contexts)

    def get_item_in_contexts(self, item_id, contexts):
        try:
            item = self.keeplist[item_id]
        except KeyError:
            return None
        else:
            phonelist = self._innerdata.xod_config['phones']
            if phonelist.is_user_id_in_contexts(item_id, contexts):
                return item
            return None
