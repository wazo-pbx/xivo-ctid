# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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

from xivo_cti.cti.commands.history import HistoryMode
from xivo_dao.cel_dao import UnsupportedLineProtocolException
from xivo_dao.data_handler.call_log import dao as call_log_dao

from .calls import Call

logger = logging.getLogger(__name__)


def history_for_phone(phone, limit):
    identifier = _phone_to_identifier(phone)
    try:
        calls = all_calls_for_phone(identifier, limit)
    except UnsupportedLineProtocolException:
        logger.warning('Could not get history for phone: %s', phone['name'])
    return calls


def all_calls_for_phone(identifier, limit):
    call_logs = call_log_dao.find_all_history_for_phone(identifier, limit)
    return _convert_all_call_logs(call_logs, identifier)


def _convert_all_call_logs(call_logs, identifier):
    all_calls = []
    for call_log in call_logs:
        if call_log.destination_line_identity == identifier:
            caller_id = call_log.source_name
            extension = call_log.source_exten
            if call_log.answered:
                mode = HistoryMode.answered
            else:
                mode = HistoryMode.missed
        else:
            caller_id = call_log.destination_name
            extension = call_log.destination_exten
            mode = HistoryMode.outgoing

        all_call = Call(call_log.date,
                        int(round(call_log.duration.total_seconds())),
                        caller_id,
                        extension,
                        mode)
        all_calls.append(all_call)
    return all_calls


def _phone_to_identifier(phone):
    return u'%s/%s' % (phone['protocol'], phone['name'])
