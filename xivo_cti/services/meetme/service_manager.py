# -*- coding: utf-8 -*-
# Copyright 2012-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import time
import logging

from copy import deepcopy
from xivo_dao.helpers.db_utils import session_scope
from xivo_dao import user_line_dao
from xivo_dao import meetme_dao

from xivo_cti.ioc.context import context
from xivo_cti.ami import ami_callback_handler

logger = logging.getLogger(__name__)

CHANNEL = 'Channel'
CONF_ROOM_NUMBER = 'Meetme'
USER = 'User'
CIDNAME = 'CallerIDName'
CIDNUMBER = 'CallerIDNum'
YES, NO = 'Yes', 'No'


def register_callbacks():
    ami_handler = ami_callback_handler.AMICallbackHandler.get_instance()
    ami_handler.register_callback('MeetmeJoin', parse_join)
    ami_handler.register_callback('MeetmeLeave', parse_leave)
    ami_handler.register_callback('MeetmeMute', parse_meetmemute)
    ami_handler.register_callback('MeetmeList', parse_meetmelist)


def parse_join(event):
    with session_scope():
        number = event[CONF_ROOM_NUMBER]
        is_a_meetme = meetme_dao.is_a_meetme(number)
    if is_a_meetme:
        context.get('meetme_service_manager').join(
            event[CHANNEL],
            number,
            int(event[USER]),
            event[CIDNAME],
            event[CIDNUMBER])


def parse_leave(event):
    with session_scope():
        number = event[CONF_ROOM_NUMBER]
        is_a_meetme = meetme_dao.is_a_meetme(number)
    if is_a_meetme:
        context.get('meetme_service_manager').leave(number, int(event[USER]))


def parse_meetmelist(event):
    with session_scope():
        number = event['Conference']
        is_a_meetme = meetme_dao.is_a_meetme(number)
    if is_a_meetme:
        context.get('meetme_service_manager').refresh(
            event[CHANNEL],
            number,
            int(event['UserNumber']),
            event['CallerIDName'],
            event['CallerIDNum'],
            event['Muted'] == YES)


def parse_meetmemute(event):
    with session_scope():
        number = event['Meetme']
        is_a_meetme = meetme_dao.is_a_meetme(number)
    if is_a_meetme:
        muting = event['Status'] == 'on'
        if muting:
            context.get('meetme_service_manager').mute(number, int(event[USER]))
        else:
            context.get('meetme_service_manager').unmute(number, int(event[USER]))


class MeetmeServiceManager(object):

    def __init__(self, meetme_service_notifier, ami_class):
        self.notifier = meetme_service_notifier
        self.ami = ami_class
        self._cache = {}

    def initialize(self):
        old_cache = deepcopy(self._cache)
        with session_scope():
            configs = meetme_dao.get_configs()
        self._cache = {}
        for config in configs:
            self._add_room(*config)
        for room, config in self._cache.iteritems():
            if room in old_cache:
                self._cache[room]['members'] = old_cache[room]['members']
        self._publish_change()

    def join(self, channel, conf_number, join_seq_number, cid_name, cid_num):
        logger.debug('Join %s %s %s %s %s', channel, conf_number, join_seq_number, cid_name, cid_num)
        if cid_num == conf_number:
            try:
                with session_scope():
                    cid_all, cid_name, cid_num = user_line_dao.get_cid_for_channel(channel)
            except (ValueError, LookupError):
                logger.info('Joining from an originate, cannot get Caller ID from this channel')

        with session_scope():
            muted = meetme_dao.muted_on_join_by_number(conf_number)

        member_status = _build_joining_member_status(join_seq_number,
                                                     cid_name,
                                                     cid_num,
                                                     channel,
                                                     muted)
        self._set_room_config(conf_number)
        if not self._has_members(conf_number):
            self._cache[conf_number]['start_time'] = time.time()
        self._cache[conf_number]['members'][join_seq_number] = member_status
        self._publish_change()

    def leave(self, conf_number, join_seq_number):
        logger.debug('Leave %s %s', conf_number, join_seq_number)
        if join_seq_number not in self._cache[conf_number]['members']:
            logger.warning('Untracked user leaving conference %s', conf_number)
            return
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
            with session_scope():
                meetme_id = meetme_dao.find_by_confno(room_number)
                config = meetme_dao.get_config(meetme_id)
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
        return bool(self._cache[room_number]['members'])

    def _has_member(self, room_number, seq_number, name, number):
        try:
            member = self._cache[room_number]['members'][seq_number]
        except KeyError:
            return False
        else:
            return member['name'] == name and member['number'] == number

    def _find_meetme_by_line(self, line_interface):
        logger.debug('Looking for line %s', line_interface)
        lowered_iface = line_interface.lower()

        for meetme_number, meetme_config in self._cache.iteritems():
            if not self._has_members(meetme_number):
                continue

            for member_order, member_status in meetme_config['members'].iteritems():
                lowered_channel = member_status['channel'].lower()
                if lowered_iface in lowered_channel:
                    return meetme_config['context'], meetme_number

        raise LookupError('No such meetme member %s', line_interface)

    def _publish_change(self):
        self.notifier.publish_meetme_update(self._cache)


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
