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

# define the events, sorted according to their class
# (classes are defined in include/asterisk/manager.h)

event_flags = dict()
event_others = dict()

event_flags['SYSTEM'] = ['Alarm', 'AlarmClear', 'SpanAlarm', 'SpanAlarmClear',
                         'Reload', 'Shutdown', 'ModuleLoadReport',
                         'FullyBooted',  # (1.8)
                         'DNDState', 'MobileStatus', 'Registry',
                         'ChannelReload', 'ChannelUpdate', 'LogChannel'
                         ]

event_flags['CALL'] = ['Dial', 'Hangup', 'Pickup', 'Rename', 'Unlink',
                       'Bridge', 'BridgeExec', 'BridgeAction',
                       'Transfer',  # only in chan_sip
                       'Hold',  # only in chan_sip and chan_iax2
                       'Masquerade', 'OriginateResponse', 'MessageWaiting', 'MiniVoiceMail',
                       'ParkedCallStatus',  # CLG addendum
                       'ParkedCall', 'UnParkedCall', 'ParkedCallTimeOut', 'ParkedCallGiveUp',
                       'ChanSpyStart', 'ChanSpyStop',
                       'DAHDIChannel',
                       'Newchannel',
                       'NewAccountCode',  # (1.8)
                       'NewCallerid',  # was 'Newcallerid' in 1.4
                       'NewPeerAccount',
                       'CEL', 'MCID',
                       'Join', 'Leave',
                       'ExtensionStatus', 'MusicOnHold',
                       'FaxSent', 'FaxReceived', 'ReceiveFAXStatus', 'SendFAXStatus', 'ReceiveFAX', 'SendFAX'
                       ]

event_flags['AGENT'] = ['AgentCalled',
                        'AgentConnect',
                        'AgentComplete',
                        'AgentDump',
                        'AgentRingNoAnswer',
                        ]

event_flags['USER'] = ['JabberEvent', 'JabberStatus', 'UserEvent' ]

event_flags['DIALPLAN'] = ['Newexten',  # in order to handle outgoing calls ?
                            'VarSet' ]

event_others['replies'] = [
    'PeerEntry', 'PeerlistComplete',  # after SIPpeers or IAXpeers or ...
    'ParkedCallsComplete',  # after ParkedCalls
    'Status' , 'StatusComplete',  # after Status
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

    'Inherit',  # (xivo) to track Local/;1 etc ... channels creation
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

manager_commands = {}

manager_commands['meta'] = [
    # general (answer is in the Response field)
    'CoreSettings', 'CoreStatus',
    'ListCommands', 'ShowDialPlan'
    ]

manager_commands['other'] = [
    'AbsoluteTimeout',
    'AgentLogoff', 'AGI', 'AOCMessage',
    'Challenge', 'Command',
    'DataGet',
    'DBDel', 'DBDelTree', 'DBGet', 'DBPut',
    'Events', 'ExtensionState',
    'Getvar',
    'JabberSend',
    'LocalOptimizeAway',
    'MailboxCount', 'MailboxStatus',
    'ModuleCheck', 'ModuleLoad',
    'Ping', 'PlayDTMF',
    'QueueAdd', 'QueueLog', 'QueuePause', 'QueuePenalty', 'QueueReload',
    'QueueRemove', 'QueueReset', 'QueueRule',
    'MuteAudio', 'Reload',
    'SendText', 'Setvar',
    'UserEvent',
    'WaitEvent',

    # Connection
    'Login', 'Logoff',

    # call actions
    'Atxfer', 'Bridge', 'Hangup', 'Originate', 'Park', 'Redirect',

    # config files
    'CreateConfig', 'GetConfigJSON', 'GetConfig', 'ListCategories', 'UpdateConfig',

    'Queues',  # this one is actually a CLI command - avoid using it

    # monitor actions
    'ChangeMonitor', 'MixMonitorMute', 'Monitor',
    'PauseMonitor', 'StopMonitor', 'UnpauseMonitor',

    # protocol-related commands
    'DAHDIDialOffhook', 'DAHDIDNDoff', 'DAHDIDNDon', 'DAHDIHangup',
    'DAHDIRestart', 'DAHDIShowChannels', 'DAHDITransfer',
    'IAXnetstats', 'IAXpeerlist',
    'SCCPDeviceAddLine', 'SCCPDeviceRestart', 'SCCPDeviceUpdate',
    'SCCPLineForwardUpdate', 'SCCPListDevices', 'SCCPListLines',
    'SKINNYshowline', 'SKINNYlines', 'SKINNYshowdevice', 'SKINNYdevices',
    'SIPnotify', 'SIPqualifypeer', 'SIPshowpeer', 'SIPshowregistry',
    ]

# list of applications
# - might be useful for all the "Originate an application" needs
# - actual list would be to be retrieved from "core show applications" or an AMI equivalent
applications = [
    'AddQueueMember', 'ADSIProg', 'AgentLogin', 'AgentMonitorOutgoing', 'AGI', 'AMD',
    'Answer', 'Authenticate', 'BackGround', 'BackgroundDetect', 'Bridge', 'Busy',
    'CallCompletionCancel', 'CallCompletionRequest', 'CELGenUserEvent', 'ChangeMonitor',
    'ChanIsAvail', 'ChannelRedirect', 'ChanSpy', 'ClearHash', 'ConfBridge', 'Congestion',
    'ContinueWhile', 'ControlPlayback', 'DAHDIBarge', 'DAHDIRAS', 'DAHDIScan', 'DateTime',
    'DBdel', 'DBdeltree', 'DeadAGI', 'Dial', 'Dictate', 'Directory', 'DISA', 'DumpChan',
    'EAGI', 'Echo', 'EndWhile', 'Exec', 'ExecIf', 'ExecIfTime', 'ExitWhile', 'ExtenSpy',
    'ExternalIVR', 'Festival', 'Flash', 'FollowMe', 'ForkCDR', 'GetCPEID', 'Gosub', 'GosubIf',
    'Goto', 'GotoIf', 'GotoIfTime', 'Hangup', 'IAX2Provision', 'ICES', 'ImportVar', 'Incomplete',
    'JabberJoin', 'JabberLeave', 'JabberSend', 'JabberSendGroup', 'JabberStatus',
    'Log', 'Macro', 'MacroExclusive', 'MacroExit', 'MacroIf', 'MailboxExists',
    'MeetMe', 'MeetMeAdmin', 'MeetMeChannelAdmin', 'MeetMeCount',
    'Milliwatt', 'MinivmAccMess', 'MinivmDelete', 'MinivmGreet', 'MinivmMWI',
    'MinivmNotify', 'MinivmRecord', 'MixMonitor', 'Monitor', 'Morsecode',
    'MP3Player', 'MSet', 'MusicOnHold', 'NBScat', 'NoCDR', 'NoOp', 'Originate',
    'Page', 'Park', 'ParkAndAnnounce', 'ParkedCall', 'PauseMonitor', 'PauseQueueMember',
    'Pickup', 'PickupChan', 'Playback', 'PlayTones', 'PrivacyManager', 'Proceeding',
    'Progress', 'Queue', 'QueueLog', 'RaiseException', 'Read', 'ReadExten', 'ReadFile',
    'ReceiveFAX', 'Record', 'RemoveQueueMember', 'ResetCDR', 'RetryDial', 'Return', 'Ringing',
    'SayAlpha', 'SayDigits', 'SayNumber', 'SayPhonetic', 'SayUnixTime', 'SendDTMF', 'SendFAX',
    'SendImage', 'SendText', 'SendURL', 'Set', 'SetAMAFlags', 'SetCallerPres', 'SetMusicOnHold',
    'SIPAddHeader', 'SIPDtmfMode', 'SIPRemoveHeader', 'SLAStation', 'SLATrunk', 'SMS', 'SoftHangup',
    'StackPop', 'StartMusicOnHold', 'StopMixMonitor', 'StopMonitor', 'StopMusicOnHold',
    'StopPlayTones', 'System', 'TestClient', 'TestServer', 'Transfer', 'TryExec', 'TrySystem',
    'UnpauseMonitor', 'UnpauseQueueMember', 'UserEvent', 'Verbose',
    'VMAuthenticate', 'VMSayName', 'VoiceMail', 'VoiceMailMain',
    'Wait', 'WaitExten', 'WaitForNoise', 'WaitForRing', 'WaitForSilence', 'WaitMusicOnHold', 'WaitUntil',
    'While', 'Zapateller'
    ]

ami_error_responses_list = ['No such channel',
                            'No such agent',
                            'Agent already logged in',
                            'Permission denied',
                            'Member not dynamic',
                            'Extension not specified',
                            'Interface not found',
                            'No active conferences.',
                            'Unable to add interface: Already there',
                            'Unable to remove interface from queue: No such queue',
                            'Unable to remove interface: Not there']

ami_success_responses_list = ['Channel status will follow',
                              'Parked calls will follow',
                              'Queue status will follow',
                              'Variable Set',
                              'Attended transfer started',
                              'Channel Hungup',
                              'Park successful',
                              'Meetme user list will follow',
                              'AOriginate successfully queued',
                              'Originate successfully queued',
                              'Redirect successful',
                              'Started monitoring channel',
                              'Stopped monitoring channel',
                              'Added interface to queue',
                              'Removed interface from queue',
                              'Interface paused successfully',
                              'Interface unpaused successfully',
                              'Agent logged out',
                              'Agent logged in']
