# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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
