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

from xivo_cti.dao.alchemy.userfeatures import UserFeatures
from xivo_cti.dao.alchemy import dbconnection
import time

logger = logging.getLogger("UserFeaturesDAO")


class UserFeaturesDAO(object):

    def __init__(self, session):
        self._session = session

    def enable_dnd(self, user_id):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablednd': 1})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['enablednd'] = True

    def disable_dnd(self, user_id):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablednd': 0})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['enablednd'] = False

    def enable_filter(self, user_id):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'incallfilter': 1})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['incallfilter'] = True

    def disable_filter(self, user_id):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'incallfilter': 0})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['incallfilter'] = False

    def enable_unconditional_fwd(self, user_id, destination):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enableunc': 1,
                                                                                     'destunc': destination})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['enableunc'] = True
        self._innerdata.xod_config['users'].keeplist[user_id]['destunc'] = destination

    def disable_unconditional_fwd(self, user_id, destination):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enableunc': 0,
                                                                                     'destunc': destination})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['destunc'] = destination
        self._innerdata.xod_config['users'].keeplist[user_id]['enableunc'] = False

    def enable_rna_fwd(self, user_id, destination):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablerna': 1,
                                                                                     'destrna': destination})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['enablerna'] = True
        self._innerdata.xod_config['users'].keeplist[user_id]['destrna'] = destination

    def disable_rna_fwd(self, user_id, destination):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablerna': 0,
                                                                                     'destrna': destination})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['destrna'] = destination
        self._innerdata.xod_config['users'].keeplist[user_id]['enablerna'] = False

    def enable_busy_fwd(self, user_id, destination):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablebusy': 1,
                                                                                     'destbusy': destination})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['enablebusy'] = True
        self._innerdata.xod_config['users'].keeplist[user_id]['destbusy'] = destination

    def disable_busy_fwd(self, user_id, destination):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablebusy': 0,
                                                                                     'destbusy': destination})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['destbusy'] = destination
        self._innerdata.xod_config['users'].keeplist[user_id]['enablebusy'] = False

    def get(self, user_id):
        res = self._session.query(UserFeatures).filter(UserFeatures.id == int(user_id))
        if res.count() == 0:
            raise LookupError
        return res[0]

    def find_by_agent_id(self, agent_id):
        res = self._session.query(UserFeatures).filter(UserFeatures.agentid == int(agent_id))
        return [user.id for user in res]

    def agent_id(self, user_id):
        return self.get(user_id).agentid

    def disconnect(self, user_id):
        userdata = self._innerdata.xod_status['users'][user_id]
        userdata['connection'] = None
        userdata['last-logouttimestamp'] = time.time()

    def set_presence(self, user_id, presence):
        userdata = self._innerdata.xod_status['users'][user_id]
        userdata['availstate'] = presence

    def is_agent(self, user_id):
        try:
            agent_id = self.agent_id(user_id)
            return agent_id is not None
        except LookupError:
            return False

    def get_profile(self, user_id):
        return self.get(user_id).profileclient

    @classmethod
    def new_from_uri(cls, uri):
        connection = dbconnection.get_connection(uri)
        return cls(connection.get_session())
