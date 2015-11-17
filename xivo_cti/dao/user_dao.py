# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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
import time

from xivo_dao.helpers.db_utils import session_scope
from xivo_dao import user_dao

from xivo_cti.exception import NoSuchUserException, NoSuchLineException

logger = logging.getLogger("UserDAO")


class UserDAO(object):

    def __init__(self, innerdata):
        self.innerdata = innerdata

    def _phone(self, phone_id):
        try:
            return self.innerdata.xod_config['phones'].keeplist[phone_id]
        except LookupError:
            raise NoSuchLineException(phone_id)

    def _user(self, user_id):
        try:
            return self.innerdata.xod_config['users'].keeplist[user_id]
        except LookupError:
            raise NoSuchUserException(user_id)

    def _user_status(self, user_id):
        try:
            return self.innerdata.xod_status['users'][user_id]
        except LookupError:
            raise NoSuchUserException(user_id)

    def enable_dnd(self, user_id):
        with session_scope():
            user_dao.enable_dnd(user_id)
        user = self._user(user_id)
        user['enablednd'] = True

    def disable_dnd(self, user_id):
        with session_scope():
            user_dao.disable_dnd(user_id)
        user = self._user(user_id)
        user['enablednd'] = False

    def enable_filter(self, user_id):
        with session_scope():
            user_dao.enable_filter(user_id)
        user = self._user(user_id)
        user['incallfilter'] = True

    def disable_filter(self, user_id):
        with session_scope():
            user_dao.disable_filter(user_id)
        user = self._user(user_id)
        user['incallfilter'] = False

    def enable_unconditional_fwd(self, user_id, destination):
        with session_scope():
            user_dao.enable_unconditional_fwd(user_id, destination)
        user = self._user(user_id)
        user['enableunc'] = True
        user['destunc'] = destination

    def disable_unconditional_fwd(self, user_id, destination):
        with session_scope():
            user_dao.disable_unconditional_fwd(user_id, destination)
        user = self._user(user_id)
        user['destunc'] = destination
        user['enableunc'] = False

    def enable_rna_fwd(self, user_id, destination):
        with session_scope():
            user_dao.enable_rna_fwd(user_id, destination)
        user = self._user(user_id)
        user['enablerna'] = True
        user['destrna'] = destination

    def disable_rna_fwd(self, user_id, destination):
        with session_scope():
            user_dao.disable_rna_fwd(user_id, destination)
        user = self._user(user_id)
        user['destrna'] = destination
        user['enablerna'] = False

    def enable_busy_fwd(self, user_id, destination):
        with session_scope():
            user_dao.enable_busy_fwd(user_id, destination)
        user = self._user(user_id)
        user['enablebusy'] = True
        user['destbusy'] = destination

    def disable_busy_fwd(self, user_id, destination):
        with session_scope():
            user_dao.disable_busy_fwd(user_id, destination)
        user = self._user(user_id)
        user['destbusy'] = destination
        user['enablebusy'] = False

    def disconnect(self, user_id):
        user_status = self._user_status(user_id)
        user_status['connection'] = None
        user_status['last-logouttimestamp'] = time.time()

    def get_presence(self, user_id):
        user_status = self._user_status(user_id)
        return user_status['availstate']

    def set_presence(self, user_id, presence):
        user_status = self._user_status(user_id)
        user_status['availstate'] = presence

    def get_fullname(self, user_id):
        user = self._user(user_id)
        return user['fullname']

    def get_line(self, user_id):
        try:
            user = self._user(user_id)
        except NoSuchUserException:
            raise

        if 'linelist' in user and user['linelist']:
            line_id = user['linelist'][0]
        else:
            raise NoSuchLineException()

        try:
            line = self._phone(line_id)
        except NoSuchLineException:
            raise

        return line

    def get_line_identity(self, user_id):
        try:
            line_interface = self.get_line(user_id)['identity']
            if '\/' in line_interface:
                line_interface = line_interface.replace('\/', '/')
        except (NoSuchUserException, NoSuchLineException):
            return None
        return line_interface

    def get_context(self, user_id):
        try:
            line = self.get_line(user_id)
        except (NoSuchUserException, NoSuchLineException):
            with session_scope():
                return user_dao.get_context(user_id)
        return line['context']

    def get_cti_profile_id(self, user_id):
        try:
            user = self._user(user_id)
        except NoSuchUserException:
            return None
        return int(user['cti_profile_id'])

    def get_agent_id(self, user_id):
        try:
            user = self._user(user_id)
        except NoSuchUserException:
            return None
        return user['agentid']
