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
        history = None
    else:
        history = _get_history_for_phone(phone, mode, size)

    if history is None:
        return 'message', {}
    else:
        return 'message', {'class': 'history', 'mode': mode, 'history': history}


def _get_history_for_phone(phone, mode, limit):
    result = []
    try:
        if mode == HistoryMode.outgoing:
            for sent_call in manager.outgoing_calls_for_phone(phone, limit):
                result.append({'calldate': sent_call.date.isoformat(),
                               'duration': sent_call.duration,
                               'fullname': sent_call.extension})
        elif mode == HistoryMode.answered:
            for received_call in manager.answered_calls_for_phone(phone, limit):
                result.append({'calldate': received_call.date.isoformat(),
                               'duration': received_call.duration,
                               'fullname': received_call.caller_name})
        elif mode == HistoryMode.missed:
            for received_call in manager.missed_calls_for_phone(phone, limit):
                result.append({'calldate': received_call.date.isoformat(),
                               'duration': received_call.duration,
                               'fullname': received_call.caller_name})
    except UnsupportedLineProtocolException:
        logger.warning('Could not get history for phone: %s', phone['name'])
    return result
