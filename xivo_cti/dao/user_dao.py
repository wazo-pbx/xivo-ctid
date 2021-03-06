# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging
import time
import uuid

from xivo_cti.database import user_db
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

    def _is_uuid(self, id_):
        try:
            uuid.UUID(id_)
            return True
        except (ValueError, AttributeError):
            return False

    def _user(self, user_id):
        users = self.innerdata.xod_config['users'].keeplist

        if user_id in users:
            return users[user_id]
        elif self._is_uuid(user_id):
            for config in users.itervalues():
                if config.get('uuid') == user_id:
                    return config

        raise NoSuchUserException(user_id)

    def _user_status(self, user_id_or_uuid):
        user_id = str(self._user(user_id_or_uuid)['id'])
        return self.innerdata.xod_status['users'][user_id]

    def get(self, id_or_uuid):
        return self._user(id_or_uuid)

    def connect(self, user_id):
        user_status = self._user_status(user_id)
        user_status['connection'] = 'yes'

    def set_dnd(self, user_id, enabled):
        user = self._user(user_id)
        user['enablednd'] = enabled

    def set_incallfilter(self, user_id, enabled):
        user = self._user(user_id)
        user['incallfilter'] = enabled

    def set_unconditional_fwd(self, user_id, enabled, destination):
        user = self._user(user_id)
        user['enableunc'] = enabled
        user['destunc'] = destination

    def set_rna_fwd(self, user_id, enabled, destination):
        user = self._user(user_id)
        user['enablerna'] = enabled
        user['destrna'] = destination

    def set_busy_fwd(self, user_id, enabled, destination):
        user = self._user(user_id)
        user['enablebusy'] = enabled
        user['destbusy'] = destination

    def disconnect(self, user_id):
        user_status = self._user_status(user_id)
        user_status['connection'] = None
        user_status['last-logouttimestamp'] = time.time()

    def get_by_uuid(self, uuid):
        for user_config in self.innerdata.xod_config['users'].keeplist.itervalues():
            if user_config['uuid'] == uuid:
                return user_config
        raise NoSuchUserException(uuid)

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
        return self.get_lines(user_id)[0]

    def get_lines(self, user_id):
        try:
            user = self._user(user_id)
        except NoSuchUserException:
            raise

        if 'linelist' in user and user['linelist']:
            line_ids = user['linelist']
        else:
            raise NoSuchLineException()

        try:
            lines = [self._phone(line_id) for line_id in line_ids]
        except NoSuchLineException:
            raise

        return lines

    def get_line_identity(self, user_id):
        try:
            line_interface = self.get_line(user_id)['identity']
            if '\/' in line_interface:
                line_interface = line_interface.replace('\/', '/')
        except (NoSuchUserException, NoSuchLineException):
            return None

        #TODO: clean after pjsip migration
        if line_interface.startswith('SIP'):
            line_interface = line_interface.replace('SIP', 'PJSIP')

        return line_interface

    def get_context(self, user_id):
        try:
            line = self.get_line(user_id)
        except (NoSuchUserException, NoSuchLineException):
            return user_db.find_line_context(user_id)
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
