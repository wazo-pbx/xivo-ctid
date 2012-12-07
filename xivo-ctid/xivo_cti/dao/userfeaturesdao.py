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

from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.userfeatures import UserFeatures
from sqlalchemy import and_
from xivo_dao import userfeatures_dao

logger = logging.getLogger("UserFeaturesDAO")

_DB_NAME = 'asterisk'


def _session():
    connection = dbconnection.get_connection(_DB_NAME)
    return connection.get_session()


class UserFeaturesDAO(object):

    def __init__(self):
        pass

    def enable_dnd(self, user_id):
        _session().query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablednd': 1})
        _session().commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['enablednd'] = True

    def disable_dnd(self, user_id):
        _session().query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablednd': 0})
        _session().commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['enablednd'] = False

    def enable_filter(self, user_id):
        _session().query(UserFeatures).filter(UserFeatures.id == user_id).update({'incallfilter': 1})
        _session().commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['incallfilter'] = True

    def disable_filter(self, user_id):
        _session().query(UserFeatures).filter(UserFeatures.id == user_id).update({'incallfilter': 0})
        _session().commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['incallfilter'] = False

    def enable_unconditional_fwd(self, user_id, destination):
        _session().query(UserFeatures).filter(UserFeatures.id == user_id).update({'enableunc': 1,
                                                                                     'destunc': destination})
        _session().commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['enableunc'] = True
        self._innerdata.xod_config['users'].keeplist[user_id]['destunc'] = destination

    def disable_unconditional_fwd(self, user_id, destination):
        _session().query(UserFeatures).filter(UserFeatures.id == user_id).update({'enableunc': 0,
                                                                                     'destunc': destination})
        _session().commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['destunc'] = destination
        self._innerdata.xod_config['users'].keeplist[user_id]['enableunc'] = False

    def enable_rna_fwd(self, user_id, destination):
        _session().query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablerna': 1,
                                                                                     'destrna': destination})
        _session().commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['enablerna'] = True
        self._innerdata.xod_config['users'].keeplist[user_id]['destrna'] = destination

    def disable_rna_fwd(self, user_id, destination):
        _session().query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablerna': 0,
                                                                                     'destrna': destination})
        _session().commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['destrna'] = destination
        self._innerdata.xod_config['users'].keeplist[user_id]['enablerna'] = False

    def enable_busy_fwd(self, user_id, destination):
        _session().query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablebusy': 1,
                                                                                     'destbusy': destination})
        _session().commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['enablebusy'] = True
        self._innerdata.xod_config['users'].keeplist[user_id]['destbusy'] = destination

    def disable_busy_fwd(self, user_id, destination):
        _session().query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablebusy': 0,
                                                                                     'destbusy': destination})
        _session().commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['destbusy'] = destination
        self._innerdata.xod_config['users'].keeplist[user_id]['enablebusy'] = False

    def disconnect(self, user_id):
        userdata = self._innerdata.xod_status['users'][user_id]
        userdata['connection'] = None
        userdata['last-logouttimestamp'] = time.time()

    def set_presence(self, user_id, presence):
        userdata = self._innerdata.xod_status['users'][user_id]
        userdata['availstate'] = presence

    def get(self, user_id):
        return userfeatures_dao.get(user_id)

    def find_by_agent_id(self, agent_id):
        return userfeatures_dao.find_by_agent_id(agent_id)

    def agent_id(self, user_id):
        return userfeatures_dao.agent_id(user_id)

    def is_agent(self, user_id):
        return userfeatures_dao.is_agent(user_id)

    def get_profile(self, user_id):
        return userfeatures_dao.get_profile(user_id)

    def get_reachable_contexts(self, user_id):
        return userfeatures_dao.get_reachable_contexts(user_id)


def all():
    return userfeatures_dao.all()


def find_by_line_id(line_id):
    return userfeatures_dao.find_by_line_id(line_id)


def get_line_identity(user_id):
    return userfeatures_dao.get_line_identity(user_id)


def get_agent_number(user_id):
    return userfeatures_dao.get_agent_number(user_id)


def get_dest_unc(user_id):
    return userfeatures_dao.get_dest_unc(user_id)


def get_fwd_unc(user_id):
    return userfeatures_dao.get_fwd_unc(user_id)


def get_dest_busy(user_id):
    return userfeatures_dao.get_dest_busy(user_id)


def get_fwd_busy(user_id):
    return userfeatures_dao.get_fwd_busy(user_id)


def get_dest_rna(user_id):
    return userfeatures_dao.get_dest_rna(user_id)


def get_fwd_rna(user_id):
    return userfeatures_dao.get_fwd_rna(user_id)


def get_name_number(user_id):
    return userfeatures_dao.get_name_number(user_id)


def get_device_id(user_id):
    return userfeatures_dao.get_device_id(user_id)
