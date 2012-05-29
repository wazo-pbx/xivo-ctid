# -*- coding: utf-8 -*-

# XiVO CTI Server
# Copyright (C) 2012  Avencall
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

from xivo_cti.dao import meetme_features_dao
import time


CHANNEL = 'Channel'
CONF_ROOM_NUMBER = 'Meetme'
ADMIN = 'Admin'
USERNUM = 'Usernum'
CIDNAME = 'CallerIDname'
CIDNUMBER = 'CallerIDnum'
YES, NO = 'Yes', 'No'


def parse_join(event):
    manager.join(
        event[CHANNEL],
        event[CONF_ROOM_NUMBER],
        event[ADMIN] != NO,
        int(event[USERNUM]),
        event[CIDNAME],
        event[CIDNUMBER])


def parse_leave(event):
    manager.leave(event[CONF_ROOM_NUMBER], int(event[USERNUM]))


class MeetmeServiceManager(object):

    def __init__(self):
        self._cache = {}

    def _initialize_configs(self):
        configs = meetme_features_dao.get_configs()
        for config in configs:
            self._add_room(*config)

    def join(self, channel, conf_number, admin, join_seq_number, cid_name, cid_num):
        member_status = _build_member_status(join_seq_number, admin, cid_name, cid_num, channel)
        self._set_room_config(conf_number)
        if not self._has_member(conf_number):
            self._cache[conf_number]['start_time'] = time.time()
        self._cache[conf_number]['members'][join_seq_number] = member_status

    def leave(self, conf_number, join_seq_number):
        self._cache[conf_number]['members'].pop(join_seq_number)
        if not self._has_member(conf_number):
            self._cache[conf_number]['start_time'] = 0

    def _set_room_config(self, room_number):
        if room_number not in self._cache:
            meetme_id = meetme_features_dao.find_by_confno(room_number)
            config = meetme_features_dao.get_config(meetme_id)
            self._add_room(*config)

    def _add_room(self, name, number, has_pin):
        if number not in self._cache:
            self._cache[number] = {}
        self._cache[number] = {'number': number,
                               'name': name,
                               'pin_required': _yes_no(has_pin),
                               'start_time': 0,
                               'members': {}}

    def _has_member(self, room_number):
        return len(self._cache[room_number]['members']) > 0


def _build_member_status(join_seq_number, is_admin, name, number, channel):
    return {'join_order': join_seq_number,
            'join_time': time.time(),
            'admin': _yes_no(is_admin),
            'number': number,
            'name': name,
            'channel': channel}


def _yes_no(is_true):
    return YES if is_true else NO


manager = MeetmeServiceManager()
