# XiVO CTI Server

# Copyright (C) 2007-2011  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

from xivo_cti.cti_anylist import AnyList
from xivo_cti.cti_config import Config

logger = logging.getLogger('userlist')


class UserList(AnyList):
    def __init__(self, newurls=[]):
        self.anylist_properties = {'name': 'users',
                                   'urloptions': (0, 11, True)}
        AnyList.__init__(self, newurls)

    def update(self):
        delta = AnyList.update(self)
        return delta

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

    def get_contexts(self, userid):
        if userid:
            userid = int(userid)
            return self.commandclass.xod_config['phones'].get_contexts_for_user(userid)
        else:
            return []

    def filter_context(self, contexts):
        if not Config.get_instance().part_context():
            return self.keeplist
        else:
            contexts = contexts if contexts else []
            ret = {}
            for user_id, user in self.keeplist.iteritems():
                user_context = self.get_contexts(user_id)
                for context in user_context:
                    if context in contexts:
                        ret[user_id] = user
            return ret
