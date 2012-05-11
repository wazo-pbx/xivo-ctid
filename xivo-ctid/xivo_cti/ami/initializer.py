# vim: set fileencoding=utf-8 :
# xivo-ctid

# Copyright (C) 2012 Avencall
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


from xivo_cti.ami.ami_callback_handler import AMICallbackHandler
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
                                                   ['PeerlistComplete'],
                                                   ['CoreShowChannelsComplete'],
                                                   ['SIPpeers', 'IAXpeers'])
    PEER_LIST_COMPLETE = InitializingEntry('PeerlistComplete',
                                           ['RegistrationsComplete'],
                                           ['PeerlistComplete'],
                                           ['SIPshowregistry', 'IAXregistry'])
    REGISTRATION_COMPLETE = InitializingEntry('RegistrationsComplete',
                                              ['DAHDIShowChannelsComplete'],
                                              ['RegistrationComplete'],
                                              ['DAHDIShowChannels'])
    DAHDI_SHOW_CHANNELS_COMPLETE = InitializingEntry('DAHDIShowChannelsComplete',
                                                     ['QueueSummaryComplete'],
                                                     ['DAHDIShowChannelsComplete'],
                                                     ['QueueSummary'])
    QUEUE_SUMMARY_COMPLETE = InitializingEntry('QueueSummaryComplete',
                                              ['QueueStatusComplete'],
                                              ['QueueSummaryComplete'],
                                              ['QueueStatus'])
    QUEUE_STATUS_COMPLETE = InitializingEntry('QueueStatusComplete',
                                              ['ParkedCallsComplete'],
                                              ['QueueStatusComplete'],
                                              ['ParkedCalls'])
    PARKED_CALLS_COMPLETE = InitializingEntry('ParkedCallsComplete',
                                              ['StatusComplete'],
                                              ['ParkedCallsComplete'],
                                              ['Status'])
    SHOW_STATUS_COMPLETE = InitializingEntry('StatusComplete',
                                             ['ShowDialPlanComplete'],
                                             ['StatusComplete'],
                                             ['ShowDialPlan'])
    SHOW_DIALPLAN_COMPLETE = InitializingEntry('ShowDialPlanComplete',
                                               ['AgentsComplete'],
                                               ['ShowDialPlanComplete'],
                                               ['Agents'])
    AGENTS_COMPLETE = InitializingEntry('AgentsComplete',
                                        ['UserEvent'],
                                        ['AgentsComplete'],
                                        ['VoicemailUsersList',
                                         'MeetmeList',
                                         ['UserEvent', [('UserEvent', 'InitComplete')]]])
    INIT_COMPLETE = InitializingEntry('UserEvent', [], ['UserEvent'], [])

    INIT_SEQUENCE = {FULLY_BOOTED.trigger: FULLY_BOOTED,
                     CORE_SHOW_CHANNEL_COMPLETE.trigger: CORE_SHOW_CHANNEL_COMPLETE,
                     PEER_LIST_COMPLETE.trigger: PEER_LIST_COMPLETE,
                     REGISTRATION_COMPLETE.trigger: REGISTRATION_COMPLETE,
                     DAHDI_SHOW_CHANNELS_COMPLETE.trigger: DAHDI_SHOW_CHANNELS_COMPLETE,
                     QUEUE_SUMMARY_COMPLETE.trigger: QUEUE_SUMMARY_COMPLETE,
                     QUEUE_STATUS_COMPLETE.trigger: QUEUE_STATUS_COMPLETE,
                     PARKED_CALLS_COMPLETE.trigger: PARKED_CALLS_COMPLETE,
                     SHOW_STATUS_COMPLETE.trigger: SHOW_STATUS_COMPLETE,
                     SHOW_DIALPLAN_COMPLETE.trigger: SHOW_DIALPLAN_COMPLETE,
                     INIT_COMPLETE.trigger: INIT_COMPLETE,
                     AGENTS_COMPLETE.trigger: AGENTS_COMPLETE}

    def __init__(self):
        self._sent_commands = []

    def register(self):
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
