# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

logger = logging.getLogger(__name__)


class StatusUpdater(object):

    def __init__(self, endpoint_status_notifier):
        self._notifier = endpoint_status_notifier

    def update_status(self, hint, status):
        phone_id = dao.phone.get_phone_id_from_hint(hint)
        if not phone_id:
            logger.warning('Failed to update phone status for {}'.format(hint))
            return

        changed = dao.phone.update_status(phone_id, status)
        if changed:
            self._notifier.notify(phone_id, status)
