# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from xivo_cti.ioc.context import context

logger = logging.getLogger(__name__)


def parse_new_caller_id(event):
    updater = context.get('channel_updater')
    updater.new_caller_id(event['Channel'], event['CallerIDName'], event['CallerIDNum'])


class ChannelUpdater(object):

    def __init__(self, innerdata):
        self.innerdata = innerdata

    def new_caller_id(self, channel, name, number):
        try:
            channel = self.innerdata.channels[channel]
        except LookupError:
            logger.info('Tried to update the caller id of an untracked channel')
        else:
            channel.set_extra_data('xivo', 'calleridname', name)
            channel.set_extra_data('xivo', 'calleridnum', number)

    def set_hold(self, channel_name, status):
        try:
            channel = self.innerdata.channels[channel_name]
        except LookupError:
            logger.warning('Tried to change the hold status on an unknown channel')
        else:
            self.innerdata.handle_cti_stack('setforce', ('channels', 'updatestatus', channel_name))
            channel.properties['holded'] = status
            self.innerdata.handle_cti_stack('empty_stack')
