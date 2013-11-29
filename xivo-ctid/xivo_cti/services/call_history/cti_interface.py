# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from xivo_cti import dao
from xivo_cti.cti.commands.history import HistoryMode
from xivo_cti.exception import NoSuchUserException, NoSuchLineException
from xivo_dao.cel_dao import UnsupportedLineProtocolException

from . import manager

logger = logging.getLogger(__name__)


def get_history(user_id, mode, size):
    try:
        phone = dao.user.get_line(user_id)
    except (NoSuchUserException, NoSuchLineException):
        return 'message', {}

    history = _get_history_for_phone(phone, mode, size)
    return 'message', {'class': 'history', 'mode': mode, 'history': history}


def _get_history_for_phone(phone, mode, limit):
    calls = []
    try:
        if mode == HistoryMode.outgoing:
            calls = manager.outgoing_calls_for_phone(phone, limit)
        elif mode == HistoryMode.answered:
            calls = manager.answered_calls_for_phone(phone, limit)
        elif mode == HistoryMode.missed:
            calls = manager.missed_calls_for_phone(phone, limit)
    except UnsupportedLineProtocolException:
        logger.warning('Could not get history for phone: %s', phone['name'])

    result = []
    for call in calls:
        result.append({'calldate': call.date.isoformat(),
                       'duration': call.duration,
                       'fullname': call.display_other_end()})
    return result
