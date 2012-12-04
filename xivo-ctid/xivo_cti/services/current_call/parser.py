# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

from xivo_cti.ami import ami_callback_handler

logger = logging.getLogger(__name__)


class CurrentCallParser(object):

    def __init__(self, current_call_manager):
        self._current_call_manager = current_call_manager

    def parse_bridge(self, event):
        if event['Bridgestate'] != 'Link':
            return

        self._current_call_manager.bridge_channels(
            event['Channel1'],
            event['Channel2']
        )

    def parse_hold(self, event):
        channel = event['Channel']
        if event['Status'] == 'On':
            self._current_call_manager.hold_channel(channel)
        else:
            self._current_call_manager.unhold_channel(channel)

    def parse_unlink(self, event):
        self._current_call_manager.unbridge_channels(
            event['Channel1'],
            event['Channel2']
        )

    def register_ami_events(self):
        logger.debug('Registering to AMI events')
        ami_handler = ami_callback_handler.AMICallbackHandler.get_instance()
        ami_handler.register_callback('Bridge', self.parse_bridge)
        ami_handler.register_callback('Hold', self.parse_hold)
        ami_handler.register_callback('Unlink', self.parse_unlink)
