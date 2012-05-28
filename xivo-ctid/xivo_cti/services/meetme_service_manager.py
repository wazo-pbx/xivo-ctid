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


def parse_join(event):
    manager.join(
        event[CHANNEL],
        event[CONF_ROOM_NUMBER],
        event[ADMIN] != 'No',
        int(event[USERNUM]),
        event[CIDNAME],
        event[CIDNUMBER])


class MeetmeServiceManager(object):

    def __init__(self):
        self._cache = {}

    def join(self, channel, conf_number, admin, join_seq_number, cid_name, cid_num):
        meetme_id = meetme_features_dao.find_by_confno(conf_number)
        now = time.time()
        self._cache = {conf_number: {'name': meetme_features_dao.get_name(meetme_id),
                                     'number': conf_number,
                                     'pin_required': _yes_no(meetme_features_dao.has_pin(meetme_id)),
                                     'start_time': now,
                                     'members': {join_seq_number: {'join_order': join_seq_number,
                                                                   'join_time': now,
                                                                   'admin': _yes_no(admin),
                                                                   'number': cid_num,
                                                                   'name': cid_name,
                                                                   'channel': channel}}}}


def _yes_no(boolean):
    return 'Yes' if boolean else 'No'


manager = MeetmeServiceManager()
