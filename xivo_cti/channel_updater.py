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

from xivo_cti.call_forms.variable_aggregator import CallFormVariable as Var
from xivo_cti.ioc.context import context

logger = logging.getLogger(__name__)


def parse_userevent(event):
    if event['UserEvent'] == 'ReverseLookup':
        updater = context.get('channel_updater')
        uniqueid = event['Uniqueid']
        updater.reverse_lookup_result(uniqueid, event)


def parse_new_caller_id(event):
    updater = context.get('channel_updater')
    updater.new_caller_id(event['Uniqueid'], event['CallerIDName'], event['CallerIDNum'])


def parse_hold(event):
    updater = context.get('channel_updater')
    updater.set_hold(event['Channel'])


def parse_unhold(event):
    updater = context.get('channel_updater')
    updater.set_unhold(event['Channel'])


def assert_has_channel(func):
    def _fn(self, channel_name, *args, **kwargs):
        if channel_name not in self.innerdata.channels:
            logger.warning('Trying to update an untracked channel %s', channel_name)
        else:
            func(self, channel_name, *args, **kwargs)
    return _fn


class ChannelUpdater(object):

    def __init__(self, innerdata, call_form_variable_aggregator):
        self.innerdata = innerdata
        self._aggregator = call_form_variable_aggregator

    def new_caller_id(self, uid, name, number):
        logger.debug('New caller ID received on channel %s: "%s" <%s>', uid, name, number)
        if name:
            self._aggregator.set(uid, Var('xivo', 'calleridname', name))
        self._aggregator.set(uid, Var('xivo', 'calleridnum', number))

    def reverse_lookup_result(self, uid, event):
        for key, value in event.iteritems():
            if key.startswith('db-'):
                key = key.split('-', 1)[-1]
                self._aggregator.set(uid, Var('db', key, value))

    @assert_has_channel
    def set_hold(self, channel_name):
        self.innerdata.channels[channel_name].properties['holded'] = True

    @assert_has_channel
    def set_unhold(self, channel_name):
        self.innerdata.channels[channel_name].properties['holded'] = False
