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

from xivo_dao.helpers.db_utils import session_scope
from xivo_dao.resources.call_log import dao as call_log_dao

from .calls import Call

logger = logging.getLogger(__name__)


class HistoryMode(object):
    answered = '1'
    missed = '2'
    outgoing = '0'


def history_for_phone(phone, limit):
    identifier = _phone_to_identifier(phone)
    return all_calls_for_phone(identifier, limit)


def all_calls_for_phone(identifier, limit):
    with session_scope():
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
