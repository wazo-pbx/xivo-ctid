#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from xivo_cti.client_connection import ClientConnection

logger = logging.getLogger("StatisticsNotifier")


class StatisticsNotifier(object):

    COMMAND_CLASS = 'getqueuesstats'
    CONTENT = 'stats'

    def __init__(self):
        self.statistic = None
        self.cti_connections = set()
        self.closed_cti_connections = set()

    def on_stat_changed(self, statistic):
        logger.info(statistic)
        self.statistic = statistic
        for cti_connection in self.cti_connections:
            self._send_statistic(cti_connection)

        for closed_connection in self.closed_cti_connections:
            self.cti_connections.remove(closed_connection)
        self.closed_cti_connections.clear()

    def subscribe(self, cti_connection):
        logger.info('xivo client subscribing ')

        if self.statistic is not None:
            cti_connection.send_message({'class': self.COMMAND_CLASS,
                                          self.CONTENT: self.statistic})

        self.cti_connections.add(cti_connection)

    def _send_statistic(self, cti_connection):
        try:
            cti_connection.send_message({'class': self.COMMAND_CLASS,
                                          self.CONTENT: self.statistic})
        except ClientConnection.CloseException:
            self.closed_cti_connections.add(cti_connection)
