# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
