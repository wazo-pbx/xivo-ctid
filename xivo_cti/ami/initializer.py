# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from collections import namedtuple

import logging

logger = logging.getLogger(__name__)

InitializingEntry = namedtuple('InitializingEntry', ['trigger', 'register', 'unregister', 'command'])


class AMIInitializer(object):

    FULLY_BOOTED = InitializingEntry('FullyBooted',
                                     ['CoreShowChannelsComplete'],
                                     [],
                                     ['CoreShowChannels'])
    CORE_SHOW_CHANNEL_COMPLETE = InitializingEntry('CoreShowChannelsComplete',
                                                   ['BridgeListComplete'],
                                                   ['CoreShowChannelsComplete'],
                                                   ['BridgeList'])
    BRIDGE_LIST_COMPLETE = InitializingEntry('BridgeListComplete',
                                             ['RegistrationsComplete'],
                                             ['BridgeListComplete'],
                                             ['SIPshowregistry', 'IAXregistry'])
    REGISTRATION_COMPLETE = InitializingEntry('RegistrationsComplete',
                                              ['DAHDIShowChannelsComplete', 'QueueSummaryComplete'],
                                              ['RegistrationsComplete', 'DAHDIShowChannelsComplete'],
                                              ['DAHDIShowChannels', 'QueueSummary'])
    QUEUE_SUMMARY_COMPLETE = InitializingEntry('QueueSummaryComplete',
                                               ['QueueStatusComplete'],
                                               ['QueueSummaryComplete'],
                                               ['QueueStatus'])
    QUEUE_STATUS_COMPLETE = InitializingEntry('QueueStatusComplete',
                                              ['StatusComplete'],
                                              ['QueueStatusComplete'],
                                              ['Status'])
    SHOW_STATUS_COMPLETE = InitializingEntry('StatusComplete',
                                             ['ShowDialPlanComplete'],
                                             ['StatusComplete'],
                                             ['ShowDialPlan'])
    SHOW_DIALPLAN_COMPLETE = InitializingEntry('ShowDialPlanComplete',
                                               ['UserEvent'],
                                               ['ShowDialPlanComplete'],
                                               ['VoicemailUsersList',
                                                'MeetmeList',
                                                ['UserEvent', [('UserEvent', 'InitComplete')]]])
    INIT_COMPLETE = InitializingEntry('UserEvent', [], ['UserEvent'], [])

    INIT_SEQUENCE = {FULLY_BOOTED.trigger: FULLY_BOOTED,
                     CORE_SHOW_CHANNEL_COMPLETE.trigger: CORE_SHOW_CHANNEL_COMPLETE,
                     BRIDGE_LIST_COMPLETE.trigger: BRIDGE_LIST_COMPLETE,
                     REGISTRATION_COMPLETE.trigger: REGISTRATION_COMPLETE,
                     QUEUE_SUMMARY_COMPLETE.trigger: QUEUE_SUMMARY_COMPLETE,
                     QUEUE_STATUS_COMPLETE.trigger: QUEUE_STATUS_COMPLETE,
                     SHOW_STATUS_COMPLETE.trigger: SHOW_STATUS_COMPLETE,
                     SHOW_DIALPLAN_COMPLETE.trigger: SHOW_DIALPLAN_COMPLETE,
                     INIT_COMPLETE.trigger: INIT_COMPLETE}

    def __init__(self):
        self._sent_commands = []

    def register(self):
        logger.debug('registering')
        self._sent_commands = []
        self._register('FullyBooted')

    def go(self, event):
        received = event.get('Event')
        if received == self.INIT_COMPLETE.trigger and event['UserEvent'] != 'InitComplete':
            return None
        if received == 'FullyBooted':
            self._sent_commands = []
        if received and received in self.INIT_SEQUENCE:
            logger.info('Initialization step %s done.', received)
            init = self.INIT_SEQUENCE[received]
            map(self._register, init.register)
            map(self._unregister, init.unregister)
            map(self._send, init.command)

    def _send(self, command):
        if command in self._sent_commands:
            return
        self._sent_commands.append(command)
        if type(command) != list:
            command = [command, []]
        logger.info('Initialization sending %s...', command[0])
        self._ami_class.sendcommand(*command)

    def _register(self, event):
        self._ami_callback_handler.register_callback(event, self.go)

    def _unregister(self, event):
        self._ami_callback_handler.unregister_callback(event, self.go)
