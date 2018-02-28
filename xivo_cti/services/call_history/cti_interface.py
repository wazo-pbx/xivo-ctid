# -*- coding: utf-8 -*-
# Copyright (C) 2007-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_cti import dao
from xivo_cti.exception import NoSuchUserException, NoSuchLineException

from . import manager

logger = logging.getLogger(__name__)


def get_history(user_id, size):
    try:
        phones = dao.user.get_lines(user_id)
    except (NoSuchUserException, NoSuchLineException):
        return 'message', {}

    calls = manager.history_for_phones(phones, size)

    history = []
    for call in calls:
        history.append({'calldate': call.date.isoformat(),
                        'duration': call.duration,
                        'fullname': call.caller_name,
                        'mode': call.mode,
                        'extension': call.extension})

    return 'message', {'class': 'history', 'history': history}
