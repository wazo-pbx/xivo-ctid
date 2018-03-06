# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
