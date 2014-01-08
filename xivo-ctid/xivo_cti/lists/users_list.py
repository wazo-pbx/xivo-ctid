# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

from xivo_cti.cti_anylist import ContextAwareAnyList


class UsersList(ContextAwareAnyList):

    def __init__(self, innerdata):
        self._innerdata = innerdata
        ContextAwareAnyList.__init__(self, 'users')

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
