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
from xivo_cti.services.meetme import service_notifier
from xivo_cti.ami import ami_callback_handler
from copy import deepcopy
import time
import logging

logger = logging.getLogger(__name__)

CHANNEL = 'Channel'
CONF_ROOM_NUMBER = 'Meetme'
USERNUM = 'Usernum'
CIDNAME = 'CallerIDname'
CIDNUMBER = 'CallerIDnum'
YES, NO = 'Yes', 'No'


def register_ami_events():
    ami_handler = ami_callback_handler.AMICallbackHandler.get_instance()
    ami_handler.register_callback('MeetmeJoin', parse_join)
    ami_handler.register_callback('MeetmeLeave', parse_leave)
    ami_handler.register_callback('MeetmeMute', parse_meetmemute)
    ami_handler.register_callback('MeetmeList', parse_meetmelist)


def parse_join(event):
    manager.join(
        event[CHANNEL],
        event[CONF_ROOM_NUMBER],
        int(event[USERNUM]),
        event[CIDNAME],
        event[CIDNUMBER])


def parse_leave(event):
    manager.leave(event[CONF_ROOM_NUMBER], int(event[USERNUM]))


def parse_meetmelist(event):
    manager.refresh(
        event[CHANNEL],
        event['Conference'],
        int(event['UserNumber']),
        event['CallerIDName'],
        event['CallerIDNum'],
        event['Muted'] == YES)


def parse_meetmemute(event):
    muting = event['Status'] == 'on'
    if muting:
        manager.mute(event['Meetme'], int(event['Usernum']))
    else:
        manager.unmute(event['Meetme'], int(event['Usernum']))


class MeetmeServiceManager(object):

    def __init__(self):
        self._cache = {}

    def initialize(self):
        logger.debug('Initializing')
        old_cache = deepcopy(self._cache)
        configs = meetme_features_dao.get_configs()
        self._cache = {}
        for config in configs:
            self._add_room(*config)
        for room, config in self._cache.iteritems():
            if room in old_cache:
                self._cache[room]['members'] = old_cache[room]['members']
        self._publish_change()

    def join(self, channel, conf_number, join_seq_number, cid_name, cid_num):
        logger.debug('Join %s %s %s %s %s', channel, conf_number, join_seq_number, cid_name, cid_num)
        member_status = _build_joining_member_status(join_seq_number,
                                                     cid_name,
                                                     cid_num,
                                                     channel,
                                                     meetme_features_dao.muted_on_join_by_number(conf_number))
        self._set_room_config(conf_number)
        if not self._has_members(conf_number):
            self._cache[conf_number]['start_time'] = time.time()
        self._cache[conf_number]['members'][join_seq_number] = member_status
        self._publish_change()

    def leave(self, conf_number, join_seq_number):
        logger.debug('Leave %s %s', conf_number, join_seq_number)
        self._cache[conf_number]['members'].pop(join_seq_number)
        if not self._has_members(conf_number):
            self._cache[conf_number]['start_time'] = 0
        self._publish_change()

    def mute(self, conf_number, join_seq_number):
        logger.debug('Mute %s %s', conf_number, join_seq_number)
        try:
            self._cache[conf_number]['members'][join_seq_number]['muted'] = True
            self._publish_change()
        except KeyError:
            logger.warning('Received a meetme mute event on an untracked conference or user')

    def unmute(self, conf_number, join_seq_number):
        logger.debug('UnMute %s %s', conf_number, join_seq_number)
        try:
            self._cache[conf_number]['members'][join_seq_number]['muted'] = False
            self._publish_change()
        except KeyError:
            logger.warning('Received a meetme unmute event on an untracked conference or user')

    def refresh(self, channel, conf_number, join_seq, cid_name, cid_num, is_muted):
        logger.debug('Refresh %s %s %s %s %s', channel, conf_number, join_seq, cid_name, cid_num)
        member_status = _build_member_status(join_seq, cid_name, cid_num, channel, is_muted)
        self._set_room_config(conf_number)
        if 'start_time' not in self._cache[conf_number] or self._cache[conf_number]['start_time'] == 0:
            self._cache[conf_number]['start_time'] = -1
        if not self._has_member(conf_number, join_seq, cid_name, cid_num):
            self._cache[conf_number]['members'][join_seq] = member_status
        self._publish_change()

    def _set_room_config(self, room_number):
        if room_number not in self._cache:
            meetme_id = meetme_features_dao.find_by_confno(room_number)
            config = meetme_features_dao.get_config(meetme_id)
            self._add_room(*config)

    def _add_room(self, name, number, has_pin, context):
        if number not in self._cache:
            self._cache[number] = {}
        self._cache[number] = {'number': number,
                               'name': name,
                               'pin_required': has_pin,
                               'start_time': 0,
                               'context': context,
                               'members': {}}

    def _has_members(self, room_number):
        return len(self._cache[room_number]['members']) > 0

    def _has_member(self, room_number, seq_number, name, number):
        try:
            member = self._cache[room_number]['members'][seq_number]
        except KeyError:
            return False
        else:
            return member['name'] == name and member['number'] == number

    def _publish_change(self):
        service_notifier.notifier.publish_meetme_update(self._cache)


def _build_joining_member_status(join_seq, name, number, channel, is_muted):
    status = _build_member_status(join_seq, name, number, channel, is_muted)
    status['join_time'] = time.time()
    return status


def _build_member_status(join_seq_number, name, number, channel, is_muted):
    return {'join_order': join_seq_number,
            'join_time': -1,
            'number': number,
            'name': name,
            'channel': channel,
            'muted': is_muted}


manager = MeetmeServiceManager()
