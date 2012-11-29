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

    def get(self, user_id):
        result = _session().query(UserFeatures).filter(UserFeatures.id == int(user_id)).first()
        if result is None:
            raise LookupError()
        return result

    def find_by_agent_id(self, agent_id):
        res = _session().query(UserFeatures).filter(UserFeatures.agentid == int(agent_id))
        return [user.id for user in res]

    def agent_id(self, user_id):
        try:
            return self.get(user_id).agentid
        except LookupError:
            return None

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

    def _get_included_contexts(self, context):
        return [line.include for line in (_session().query(ContextInclude.include)
                                           .filter(ContextInclude.context == context))]

    def _get_nested_contexts(self, contexts):
        checked = []
        to_check = set(contexts) - set(checked)
        while to_check:
            context = to_check.pop()
            contexts.extend(self._get_included_contexts(context))
            checked.append(context)
            to_check = set(contexts) - set(checked)

        return list(set(contexts))

    def get_reachable_contexts(self, user_id):
        line_contexts = [line.context for line in (_session().query(LineFeatures)
                                                    .filter(LineFeatures.iduserfeatures == user_id))]

        return self._get_nested_contexts(line_contexts)


def find_by_line_id(line_id):
    return _session().query(LineFeatures.iduserfeatures).filter(LineFeatures.id == line_id)[0].iduserfeatures


def get_line_identity(user_id):
    try:
        line = (_session().query(LineFeatures.protocol, LineFeatures.name)
                         .filter(LineFeatures.iduserfeatures == user_id))[0]
    except IndexError:
        raise LookupError('Could not find a line for user %s', user_id)
    else:
        return '%s/%s' % (line.protocol, line.name)


def get_agent_number(user_id):
    return (_session().query(AgentFeatures.number, UserFeatures.agentid)
            .filter(and_(UserFeatures.id == user_id,
                           AgentFeatures.id == UserFeatures.agentid))[0].number)


def get_dest_unc(user_id):
    return _session().query(UserFeatures.destunc).filter(UserFeatures.id == int(user_id))[0].destunc


def get_fwd_unc(user_id):
    return (_session().query(UserFeatures.enableunc).filter(UserFeatures.id == int(user_id))[0].enableunc == 1)


def get_dest_busy(user_id):
    return _session().query(UserFeatures.destbusy).filter(UserFeatures.id == int(user_id))[0].destbusy


def get_fwd_busy(user_id):
    return (_session().query(UserFeatures.enablebusy).filter(UserFeatures.id == int(user_id))[0].enablebusy == 1)


def get_dest_rna(user_id):
    return _session().query(UserFeatures.destrna).filter(UserFeatures.id == int(user_id))[0].destrna


def get_fwd_rna(user_id):
    return (_session().query(UserFeatures.enablerna).filter(UserFeatures.id == int(user_id))[0].enablerna == 1)


def get_name_number(user_id):
    res = (_session().query(UserFeatures.firstname, UserFeatures.lastname, LineFeatures.number).
           filter(and_(UserFeatures.id == LineFeatures.iduserfeatures, UserFeatures.id == user_id)))[0]
    return '%s %s' % (res.firstname, res.lastname), res.number


def get_device_id(user_id):
    row = (_session()
           .query(LineFeatures.iduserfeatures, LineFeatures.device)
           .filter(LineFeatures.iduserfeatures == user_id)).first()

    if not row:
        raise LookupError('Cannot find a device from this user id %s' % user_id)

    return int(row.device)
