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

import uuid

from xivo_cti.cti.cti_command import CTICommandClass


def _check_valid_uuid(value):
    uuid.UUID(value)
    return value


def _check_positive_int(value):
    if not isinstance(value, int):
        raise ValueError('expected int: was {}'.format(type(value)))
    if not value > 0:
        raise ValueError('expected a positive int: was {}'.format(value))
    return value


def _parse(msg, command):
    command.alias = msg['alias']
    command.remote_xivo_uuid = _check_valid_uuid(msg['to'][0])
    command.remote_user_id = _check_positive_int(msg['to'][1])
    command.text = msg['text']

Chat = CTICommandClass('chitchat', None, _parse)
Chat.add_to_registry()
