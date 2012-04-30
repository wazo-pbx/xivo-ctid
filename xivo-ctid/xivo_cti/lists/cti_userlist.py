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
        # a dictionary where keys are user id (string) and values are
        # (<alarm clock>, <timezone) tuple
        self.alarm_clk_changes = {}

    def update(self):
        delta = AnyList.update(self)
        self._update_alarm_clock_changes(delta)
        return delta

    def _update_alarm_clock_changes(self, delta):
        delta_add = delta.get('add')
        if delta_add:
            for id in delta_add:
                # ignore 'remote user'
                if not id.startswith('cs:'):
                    user = self.keeplist[id]
                    # cjson workaround
                    fixed_timezone = user['timezone'].replace('\\/', '/')
                    user['timezone'] = fixed_timezone
                    self.alarm_clk_changes[id] = (user['alarmclock'], fixed_timezone)

        delta_del = delta.get('del')
        if delta_del:
            for id in delta_del:
                # ignore 'remote user'
                if not id.startswith('cs:'):
                    self.alarm_clk_changes[id] = ('', '')

        delta_change = delta.get('change')
        if delta_change:
            for id, changed_keys in delta_change.iteritems():
                # ignore 'remote user'
                if not id.startswith('cs:'):
                    if 'alarmclock' in changed_keys or 'timezone' in changed_keys:
                        user = self.keeplist[id]
                        # cjson workaround
                        fixed_timezone = user['timezone'].replace('\\/', '/')
                        user['timezone'] = fixed_timezone
                        self.alarm_clk_changes[id] = (user['alarmclock'], fixed_timezone)

    def update_noinput(self):
        newuserlist = self.commandclass.getuserslist()
        for a, b in newuserlist.iteritems():
            if a not in self.keeplist:
                self.keeplist[a] = b

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

    def adduser(self, inparams):
        username = inparams['user']
        if not username in self.keeplist:
            self.keeplist[username] = {}
            for f in self.commandclass.userfields:
                self.keeplist[username][f] = inparams[f]

    def deluser(self, username):
        if username in self.keeplist:
            self.keeplist.pop(username)

    def get_contexts(self, userid):
        phones = self.commandclass.xod_config['phones'].keeplist
        return [phone['context'] for phone in phones.itervalues() if userid and int(userid) == int(phone['iduserfeatures'])]

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

    def find_by_agent_id(self, agent_id):
        try:
            return [user for user in self.keeplist.itervalues() if user['agentid'] == agent_id][0]
        except Exception:
            logger.warning('Could not find a user with agent id %s', agent_id)
