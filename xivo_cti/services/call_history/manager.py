# -*- coding: utf-8 -*-
# Copyright 2007-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_dao.helpers.db_utils import session_scope
from xivo_dao.resources.call_log import dao as call_log_dao

from .calls import Call

logger = logging.getLogger(__name__)


class HistoryMode(object):
    answered = '1'
    missed = '2'
    outgoing = '0'


def history_for_phones(phones, limit):
    identifiers = [_phone_to_identifier(phone) for phone in phones]
    return all_calls_for_phones(identifiers, limit)


def all_calls_for_phones(identifiers, limit):
    with session_scope():
        call_logs = call_log_dao.find_all_history_for_phones(identifiers, limit)
        return _convert_all_call_logs(call_logs, identifiers)


def _convert_all_call_logs(call_logs, identifiers):
    all_calls = []
    for call_log in call_logs:
        if call_log.destination_line_identity in identifiers:
            caller_id = call_log.source_name
            extension = call_log.source_exten
            if call_log.date_answer:
                mode = HistoryMode.answered
            else:
                mode = HistoryMode.missed
        else:
            caller_id = call_log.destination_name
            extension = call_log.destination_exten
            mode = HistoryMode.outgoing

        duration = 0
        if call_log.date_answer and call_log.date_end:
            duration = int(round((call_log.date_end - call_log.date_answer).total_seconds()))

        all_call = Call(call_log.date,
                        duration,
                        caller_id,
                        extension,
                        mode)
        all_calls.append(all_call)
    return all_calls


def _phone_to_identifier(phone):
    return u'%s/%s' % (phone['protocol'], phone['name'])
