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
from xivo_cti.client_connection import ClientConnection

logger = logging.getLogger("StatisticsNotifier")


class StatisticsNotifier(object):

    COMMAND_CLASS = 'getqueuesstats'
    CONTENT = 'stats'

    def __init__(self, cti_group_factory):
        self._cti_group = cti_group_factory.new_cti_group()

    def on_stat_changed(self, statistic):
        msg = self._new_msg(statistic)
        self._cti_group.send_message(msg)

    def subscribe(self, cti_connection):
        self._cti_group.add(cti_connection)

    def send_statistic(self, statistic, cti_connection):
        msg = self._new_msg(statistic)
        try:
            cti_connection.send_message(msg)
        except ClientConnection.CloseException:
            pass

    def _new_msg(self, statistic):
        return {'class': self.COMMAND_CLASS, self.CONTENT: statistic}
