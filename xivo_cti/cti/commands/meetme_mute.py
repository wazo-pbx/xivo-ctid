# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _check_alphanumeric_input(value):
    if not isinstance(value, basestring):
        raise ValueError('expected basestring: was {}'.format(type(value)))
    if not value.isalnum():
        raise ValueError('expected alphanumeric string: was {}'.format(value))


def _parse(msg, command):
    meetme_number, user_position = msg['functionargs']
    _check_alphanumeric_input(meetme_number)
    _check_alphanumeric_input(user_position)
    command.meetme_number = meetme_number
    command.user_position = user_position


def _match_mute(msg):
    return msg['command'] == 'meetme' and msg['function'] == 'MeetmeMute'


def _match_unmute(msg):
    return msg['command'] == 'meetme' and msg['function'] == 'MeetmeUnmute'

MeetmeMute = CTICommandClass('ipbxcommand', _match_mute, _parse)
MeetmeUnmute = CTICommandClass('ipbxcommand', _match_unmute, _parse)
MeetmeMute.add_to_registry()
MeetmeUnmute.add_to_registry()
