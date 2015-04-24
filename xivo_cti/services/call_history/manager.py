# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

from .calls import ReceivedCall, SentCall

logger = logging.getLogger(__name__)


def history_for_phone(phone, mode, limit):
    identifier = _phone_to_identifier(phone)
    calls = []
    try:
        if mode == HistoryMode.outgoing:
            calls = outgoing_calls_for_phone(identifier, limit)
        elif mode == HistoryMode.answered:
            calls = answered_calls_for_phone(identifier, limit)
        elif mode == HistoryMode.missed:
            calls = missed_calls_for_phone(identifier, limit)
    except UnsupportedLineProtocolException:
        logger.warning('Could not get history for phone: %s', phone['name'])
    return calls


def answered_calls_for_phone(identifier, limit):
    call_logs = call_log_dao.find_all_answered_for_phone(identifier, limit)
    return _convert_incoming_call_logs(call_logs)


def missed_calls_for_phone(identifier, limit):
    call_logs = call_log_dao.find_all_missed_for_phone(identifier, limit)
    return _convert_incoming_call_logs(call_logs)


def outgoing_calls_for_phone(identifier, limit):
    call_logs = call_log_dao.find_all_outgoing_for_phone(identifier, limit)
    return _convert_outgoing_call_logs(call_logs)


def _convert_incoming_call_logs(call_logs):
    received_calls = []
    for call_log in call_logs:
        caller_id = call_log.source_name
        extension = call_log.source_exten
        received_call = ReceivedCall(call_log.date,
                                     int(round(call_log.duration.total_seconds())),
                                     caller_id,
                                     extension)
        received_calls.append(received_call)
    return received_calls


def _convert_outgoing_call_logs(call_logs):
    sent_calls = []
    for call_log in call_logs:
        sent_call = SentCall(call_log.date,
                             int(round(call_log.duration.total_seconds())),
                             call_log.destination_exten)
        sent_calls.append(sent_call)
    return sent_calls


def _phone_to_identifier(phone):
    return u'%s/%s' % (phone['protocol'], phone['name'])
