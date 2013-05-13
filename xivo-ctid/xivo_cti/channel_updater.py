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


def parse_hold(event):
    logger.debug('Parse hold %s', event)
    updater = context.get('channel_updater')
    updater.set_hold(event['Channel'], event['Status'] == 'On')


def parse_inherit(event):
    updater = context.get('channel_updater')
    updater.inherit_channels(event['Parent'], event['Child'])


def assert_has_channel(func):
    def _fn(self, channel_name, *args, **kwargs):
        if channel_name not in self.innerdata.channels:
            logger.warning('Trying to update an untracked channel %s', channel_name)
        else:
            func(self, channel_name, *args, **kwargs)
    return _fn


def notify_clients(func):
    def _fn(self, channel_name, *args, **kwargs):
        self.innerdata.handle_cti_stack('setforce', ('channels', 'updatestatus', channel_name))
        func(self, channel_name, *args, **kwargs)
        self.innerdata.handle_cti_stack('empty_stack')
    return _fn


class ChannelUpdater(object):

    def __init__(self, innerdata):
        self.innerdata = innerdata

    @assert_has_channel
    def new_caller_id(self, channel_name, name, number):
        channel = self.innerdata.channels[channel_name]
        channel.set_extra_data('xivo', 'calleridname', name)
        channel.set_extra_data('xivo', 'calleridnum', number)

    @assert_has_channel
    @notify_clients
    def set_hold(self, channel_name, status):
        self.innerdata.channels[channel_name].properties['holded'] = status

    def inherit_channels(self, parent_name, child_name):
        if parent_name not in self.innerdata.channels:
            logger.warning('Received inherit event on untracked parent channel')
            return

        child_names = [child_name]
        if child_name.startswith('Local'):
            end = child_name[-1]
            other_end = '1' if end == '2' else '2'
            other_channel = child_name[:-1] + other_end
            child_names.append(other_channel)

        parent = self.innerdata.channels[parent_name]
        for child_name in child_names:
            if child_name not in self.innerdata.channels:
                logger.warning('Received inherit event on untracked child channel')
                continue
            child = self.innerdata.channels[child_name]
            child.inherit(parent)
