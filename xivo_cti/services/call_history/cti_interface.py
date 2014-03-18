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

from xivo_cti import dao
from xivo_cti.exception import NoSuchUserException, NoSuchLineException

from . import manager

logger = logging.getLogger(__name__)


def get_history(user_id, mode, size):
    try:
        phone = dao.user.get_line(user_id)
    except (NoSuchUserException, NoSuchLineException):
        return 'message', {}

    calls = manager.history_for_phone(phone, mode, size)

    history = []
    for call in calls:
        history.append({'calldate': call.date.isoformat(),
                        'duration': call.duration,
                        'fullname': call.display_other_end()})

    return 'message', {'class': 'history', 'mode': mode, 'history': history}
