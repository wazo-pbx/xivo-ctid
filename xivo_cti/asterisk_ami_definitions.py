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

# define the events, sorted according to their class
# (classes are defined in include/asterisk/manager.h)

event_flags = dict()
event_others = dict()

event_flags['SYSTEM'] = ['Alarm', 'AlarmClear', 'SpanAlarm', 'SpanAlarmClear',
                         'Reload', 'Shutdown',
                         'FullyBooted',  # (1.8)
                         'DNDState', 'MobileStatus', 'Registry',
                         'ChannelReload', 'LogChannel'
                         ]

event_flags['CALL'] = ['Dial', 'Hangup', 'Pickup', 'Rename',
                       'Bridge', 'BridgeExec', 'BridgeAction',
                       'Transfer',  # only in chan_sip
                       'Masquerade', 'OriginateResponse', 'MessageWaiting', 'MiniVoiceMail',
                       'ParkedCallStatus',  # CLG addendum
                       'ParkedCall', 'UnParkedCall', 'ParkedCallTimeOut', 'ParkedCallGiveUp',
                       'ChanSpyStart', 'ChanSpyStop',
                       'DAHDIChannel',
                       'Newchannel',
                       'NewAccountCode',  # (1.8)
                       'NewCallerid',  # was 'Newcallerid' in 1.4
                       'CEL', 'MCID',
                       'QueueCallerJoin', 'QueueCallerLeave',
                       'ExtensionStatus', 'MusicOnHold',
                       'FaxSent', 'FaxReceived', 'ReceiveFAXStatus', 'SendFAXStatus', 'ReceiveFAX', 'SendFAX'
                       ]

event_flags['AGENT'] = ['AgentCalled',
                        'AgentConnect',
                        'AgentComplete',
                        'AgentDump',
                        'AgentRingNoAnswer',
                        ]

event_flags['USER'] = ['JabberEvent', 'JabberStatus', 'UserEvent']

event_flags['DIALPLAN'] = ['Newexten',  # in order to handle outgoing calls ?
                           'VarSet']

event_others['replies'] = [
    'PeerEntry', 'PeerlistComplete',  # after SIPpeers or IAXpeers or ...
    'ParkedCallsComplete',  # after ParkedCalls
    'Status', 'StatusComplete',  # after Status
    'QueueParams', 'QueueEntry', 'QueueStatusComplete',  # after QueueStatus
    'QueueSummary', 'QueueSummaryComplete',  # after QueueSummary
    'CoreShowChannel', 'CoreShowChannelsComplete',  # after CoreShowChannels
    'RegistryEntry', 'RegistrationsComplete',  # in reply to IAXregistry / SIPshowregistry seems to go elsewhere
    'VoicemailUserEntry', 'VoicemailUserEntryComplete',  # in reply to VoicemailUsersList ? XXX when empty
    'ListDialplan', 'ShowDialPlanComplete',  # in reply to ShowDialPlan
    'DAHDIShowChannels', 'DAHDIShowChannelsComplete',  # in reply to DAHDIShowChannels

    'LineEntry', 'LinelistComplete',  # in reply to SKINNYlines
    'DeviceEntry', 'DevicelistComplete',  # in reply to SKINNYdevices

    'WaitEventComplete',
    'Placeholder', 'DBGetResponse', 'DBGetComplete',
    'DataGet Tree'
]

event_others['extra'] = [
    'Atxfer',  # (patch to fetch ?)
    'ActionRequest',  # (xivo)

    'HangupRequest',  # (xivo) to know who 'ordered' the hangup (patch submitted to digium in #0018226)
    'SoftHangupRequest',  # (xivo) to know when the hangup was requested from the CLI (patch submitted to digium in #0018226)
]
# event_others['extra'] = []

evfunction_to_method_name = dict()

# define the handling method for event XyZ to be ami_xyz()

for k, v in event_flags.iteritems():
    for eventname in v:
        # '-' to '_' for 'AOC-[DES]' events
        methodname = 'ami_%s' % eventname.lower().replace('-', '_')
        if eventname not in evfunction_to_method_name:
            evfunction_to_method_name[eventname] = methodname

for k, v in event_others.iteritems():
    for eventname in v:
        # ' ' to '_' for 'DataGet Tree' event
        methodname = 'ami_%s' % eventname.lower().replace(' ', '_')
        if eventname not in evfunction_to_method_name:
            evfunction_to_method_name[eventname] = methodname
