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

from xivo_cti.ami import ami_callback_handler

logger = logging.getLogger(__name__)


class CurrentCallParser(object):

    def __init__(self, current_call_manager):
        self._current_call_manager = current_call_manager

    def parse_hold(self, event):
        channel = event['Channel']
        self._current_call_manager.hold_channel(channel)

    def parse_unhold(self, event):
        channel = event['Channel']
        self._current_call_manager.unhold_channel(channel)

    def parse_hangup(self, event):
        self._current_call_manager.end_call(event['Channel'])
        self._current_call_manager.remove_transfer_channel(event['Channel'])

    def parse_masquerade(self, event):
        self._current_call_manager.masquerade(
            event['Original'],
            event['Clone']
        )

    def parse_varset_transfername(self, event):
        if 'Variable' not in event or event['Variable'] != 'TRANSFERERNAME':
            return

        self._current_call_manager.set_transfer_channel(
            event['Value'],
            event['Channel'],
        )

    def register_ami_events(self):
        logger.debug('Registering to AMI events')
        ami_handler = ami_callback_handler.AMICallbackHandler.get_instance()
        ami_handler.register_callback('Hold', self.parse_hold)
        ami_handler.register_callback('Unhold', self.parse_unhold)
        ami_handler.register_callback('Hangup', self.parse_hangup)
        ami_handler.register_callback('Masquerade', self.parse_masquerade)
        ami_handler.register_callback('VarSet', self.parse_varset_transfername)
