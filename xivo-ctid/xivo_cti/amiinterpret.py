# vim: set fileencoding=utf-8 :
# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall
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

import logging
import random
import string
import time

from xivo_cti import cti_config

ALPHANUMS = string.uppercase + string.lowercase + string.digits

logger = logging.getLogger('AMI_1.8')


class AMI_1_8(object):

    userevents = ('Feature',
                  'OutCall',
                  'Custom',
                  'LocalCall',
                  'dialplan2cti',
                  'LookupDirectory',
                  'User',
                  'Queue',
                  'Group',
                  'Meetme',
                  'Did',)

    def __init__(self, ctiserver, ipbxid):
        self._ctiserver = ctiserver
        self.ipbxid = ipbxid
        self.innerdata = self._ctiserver.safe.get(self.ipbxid)
        fagiport = (cti_config.Config.get_instance().getconfig('main')
                    .get('incoming_tcp').get('FAGI')[1])
        self.fagiportstring = ':%s/' % fagiport

    def ami_fullybooted(self, event):
        if self.ipbxid == self._ctiserver.myipbxid:
            self._ctiserver.myami[self.ipbxid].initrequest(0)

    def ami_newstate(self, event):
        self.innerdata.newstate(event['Channel'], event['ChannelState'])

    def ami_newchannel(self, event):
        channel = event['Channel']
        channelstate = event['ChannelState']
        context = event['Context']
        actionid = 'nc:%s' % ''.join(random.sample(ALPHANUMS, 10))
        params = {'mode': 'newchannel',
                  'amicommand': 'getvar',
                  'amiargs': [channel, 'XIVO_ORIGACTIONID']}
        self._ctiserver.myami.get(self.ipbxid).execute_and_track(actionid, params)
        self.innerdata.newchannel(channel, context, channelstate, event)

    def ami_newcallerid(self, event):
        self.innerdata.update_parking_cid(event['Channel'], event['CallerIDName'], event['CallerIDNum'])

    def ami_newexten(self, event):
        application = event['Application']
        appdata = event['AppData']
        channel = event['Channel']
        if application == 'AGI':
            if self.fagiportstring in appdata:  # match against ~ ':5002/' in appdata
                # warning : this might cause problems if AMI not connected
                if self.innerdata.fagi_sync('get', channel, 'agi'):
                    self.innerdata.fagi_sync('clear', channel)
                    self.innerdata.fagi_handle(channel, 'AMI')
                else:
                    self.innerdata.fagi_sync('set', channel, 'ami')

    def ami_hangup(self, event):
        channel = event.pop('Channel')
        #  0 - Unknown
        #  3 - No route to destination
        # 16 - Normal Clearing
        # 17 - User busy (see Orig #5)
        # 18 - No user responding (see Orig #1)
        # 19 - User alerting, no answer (see Orig #8, Orig #3, Orig #1 (soft hup))
        # 21 - Call rejected (attempting *8 when noone to intercept)
        # 24 - "lost" Call suspended
        # 27 - Destination out of order
        # 28 - Invalid number format (incomplete number)
        # 34 - Circuit/channel congestion
        self.innerdata.hangup(channel)
        self.innerdata.sheetsend('hangup', channel)

    def ami_dial(self, event):
        channel = event['Channel']
        subevent = event['SubEvent']
        if subevent == 'Begin' and 'Destination' in event:
            destination = event['Destination']
            if channel in self.innerdata.channels:
                self.innerdata.channels[channel].properties['direction'] = 'out'
                self.innerdata.channels[channel].properties['commstatus'] = 'calling'
                self.innerdata.channels[channel].properties['timestamp'] = time.time()
                self.innerdata.setpeerchannel(channel, destination)
                self.innerdata.update(channel)
            if destination in self.innerdata.channels:
                self.innerdata.channels[destination].properties['direction'] = 'in'
                self.innerdata.channels[destination].properties['commstatus'] = 'ringing'
                self.innerdata.channels[destination].properties['timestamp'] = time.time()
                self.innerdata.setpeerchannel(destination, channel)
                self.innerdata.update(destination)
            self.innerdata.sheetsend('dial', channel)

    def ami_extensionstatus(self, event):
        self.innerdata.updatehint(event['Hint'], event['Status'])

    def ami_bridge(self, event):
        channel1 = event['Channel1']
        channel2 = event['Channel2']
        if channel1 in self.innerdata.channels:
            self.innerdata.channels[channel1].properties['talkingto_kind'] = 'channel'
            self.innerdata.channels[channel1].properties['talkingto_id'] = channel2
            self.innerdata.channels[channel1].properties['timestamp'] = time.time()
            self.innerdata.channels[channel1].properties['commstatus'] = 'linked-caller'
            self.innerdata.setpeerchannel(channel1, channel2)
            self.innerdata.update(channel1)
        if channel2 in self.innerdata.channels:
            self.innerdata.channels[channel2].properties['talkingto_kind'] = 'channel'
            self.innerdata.channels[channel2].properties['talkingto_id'] = channel1
            self.innerdata.channels[channel2].properties['timestamp'] = time.time()
            self.innerdata.channels[channel2].properties['commstatus'] = 'linked-called'
            self.innerdata.setpeerchannel(channel2, channel1)
            self.innerdata.update(channel2)

    def ami_unlink(self, event):
        self.innerdata.sheetsend('unlink', event['Channel1'])

    def ami_masquerade(self, event):
        original = event['Original']
        clone = event['Clone']
        self.innerdata.masquerade(original, clone)
        self.innerdata.update_parking_parked(original, clone)

    def ami_hold(self, event):
        channel_name = event['Channel']
        status = event['Status'] == 'On'
        if channel_name in self.innerdata.channels:
            channel = self.innerdata.channels[channel_name]
            channel.properties['holded'] = status
            logger.debug('%s on hold(%s)', channel_name, status)
            if not channel.peerchannel:
                '''Usualy means that we are an agent which uses 3 channels'''
                try:
                    phone = self.innerdata.xod_config['phones'].find_phone_by_channel(channel_name)
                    agent = self.innerdata.xod_config['agents'].get_agent_by_user(phone['iduserfeatures'])
                    chan_start = 'Agent/%s' % agent['number']
                    for chan in self.innerdata.channels:
                        if chan_start in chan:
                            self.innerdata.channels[chan].properties['holded'] = status
                            logger.debug('%s on hold(%s)', chan, status)
                except:
                    logger.warning('Could not find %s peer channel to put it on hold', channel_name)

    def ami_channelupdate(self, event):
        # could be especially useful when there is a trunk : links callno-remote and callno-local
        # when the call is outgoing, one never receives the callno-remote
        channeltype = event['Channeltype']
        if channeltype == 'IAX2':
            logger.info('ami_channelupdate %s : %s - %s : %s',
                        channeltype, event['IAX2-callno-local'],
                        event['IAX2-callno-remote'],
                        event)

    def ami_originateresponse(self, event):
        channel = event['Channel']
        actionid = event.get('ActionID')
        reason = event['Reason']
        # reasons ...
        # 4 : Success
        # 0 : 1st phone unregistered
        # 1 : CLI 'channel request hangup' on the 1st phone's channel
        # 5 : 1st phone rejected the call (reject button or all lines busy)
        # 8 : 1st phone did not answer early enough
        if actionid in self._ctiserver.myami.get(self.ipbxid).originate_actionids:
            properties = self._ctiserver.myami.get(self.ipbxid).originate_actionids.pop(actionid)
            request = properties.get('request')
            cn = request.get('requester')
            try:
                cn.reply({'class': 'ipbxcommand',
                          'command': request.get('ipbxcommand'),
                          'replyid': request.get('commandid'),
                          'channel': channel,
                          'originatereason': reason})
            except Exception:
                # when requester is not connected any more ...
                pass
        else:
            logger.warning('ami_originateresponse %s %s %s %s (not in list)',
                           actionid, channel, reason, event)

    def ami_meetmejoin(self, event):
        opts = {'usernum': event['Usernum'],
                'pseudochan': event['PseudoChan'],
                'admin': 'Yes' in event['Admin'],
                'authed': 'No' in event['NoAuthed'],
                'displayname': event['CallerIDname'],
                'phonenumber': event['CallerIDnum'], }
        return self.innerdata.meetmeupdate(event['Meetme'],
                                           event['Channel'],
                                           opts)

    def ami_meetmeleave(self, event):
        opts = {'usernum': event['Usernum'], 'leave': True, }
        return self.innerdata.meetmeupdate(event['Meetme'],
                                           event['Channel'],
                                           opts)

    def ami_meetmeend(self, event):
        return self.innerdata.meetmeupdate(event['Meetme'])

    def ami_meetmemute(self, event):
        opts = {'muted': 'on' in event['Status'],
                'usernum': event['Usernum'], }
        return self.innerdata.meetmeupdate(event['Meetme'],
                                           event['Channel'],
                                           opts)

    def ami_meetmenoauthed(self, event):
        opts = {'usernum': event['Usernum'],
                'authed': 'off' in event['Status'], }
        return self.innerdata.meetmeupdate(event['Meetme'],
                                           event['Channel'],
                                           opts)

    def ami_meetmepause(self, event):
        opts = {'paused': 'on' in event['Status'], }
        return self.innerdata.meetmeupdate(event['Meetme'], opts=opts)

    def ami_join(self, event):
        self.innerdata.queueentryupdate(event['Queue'],
                                        event['Channel'],
                                        event['Position'],
                                        time.time())

    def ami_leave(self, event):
        self.innerdata.queueentryupdate(event['Queue'],
                                        event['Channel'],
                                        event['Position'])

    def ami_queuemember(self, event):
        self.innerdata.queuememberupdate(event['Queue'],
                                         event['Location'],
                                         (event['Status'],
                                          event['Paused'],
                                          event['Membership'],
                                          event['CallsTaken'],
                                          event['Penalty'],
                                          event['LastCall']))
        self.queuemember_service_manager.update_one_queuemember(event)

    def ami_queueentry(self, event):
        timestart = self.timeconvert(event['Wait'])
        self.innerdata.queueentryupdate(event['Queue'],
                                        event['Channel'],
                                        event['Position'],
                                        timestart)

    def ami_queuememberstatus(self, event):
        self.innerdata.queuememberupdate(event['Queue'],
                                         event['Location'],
                                         (event['Status'],
                                          event['Paused'],
                                          event['Membership'],
                                          event['CallsTaken'],
                                          event['Penalty'],
                                          event['LastCall']))
        self.queuemember_service_manager.update_one_queuemember(event)

    def ami_queuememberadded(self, event):
        self.ami_queuememberstatus(event)
        self.queuemember_service_manager.add_dynamic_queuemember(event)

    def ami_queuememberremoved(self, event):
        self.innerdata.queuememberupdate(event['Queue'], event['Location'])
        self.queuemember_service_manager.remove_dynamic_queuemember(event)

    def ami_queuememberpaused(self, event):
        self.innerdata.queuememberupdate(event['Queue'], event['Location'], (event['Paused'],))
        self.queuemember_service_manager.toggle_pause(event)

    def ami_agentlogin(self, event):
        self.innerdata.agentlogin(event['Agent'], event['Channel'])

    def ami_agentlogoff(self, event):
        self.innerdata.agentlogout(event['Agent'])

    def ami_agentcallbacklogin(self, event):
        self.innerdata.agentlogin(event['Agent'], event['Loginchan'])

    def ami_agentcallbacklogoff(self, event):
        self.innerdata.agentlogout(event['Agent'])

    def ami_parkedcall(self, event):
        channel = event['Channel']
        exten = event['Exten']
        parkinglot = event['Parkinglot']
        if parkinglot.startswith('parkinglot_'):
            parkinglot = '_'.join(parkinglot.split('_')[1:])
        parkingevent = {
            'parker': event.pop('From'),
            'parked': channel,
            'exten': exten,
            'cid_name': event.pop('CallerIDName'),
            'cid_num': event.pop('CallerIDNum'),
            'parktime': time.time(),
            }
        self.innerdata.update_parking(parkinglot, exten, parkingevent)
        if channel in self.innerdata.channels:
            self.innerdata.channels[channel].setparking(exten, parkinglot)

    def ami_unparkedcall(self, event):
        channel = event['Channel']
        if channel in self.innerdata.channels:
            self.innerdata.channels[channel].unsetparking()
        self.innerdata.unpark(channel)

    def ami_parkedcalltimeout(self, event):
        channel = event['Channel']
        if channel in self.innerdata.channels:
            self.innerdata.channels[channel].unsetparking()
        self.innerdata.unpark(channel)

    def ami_parkedcallgiveup(self, event):
        self.innerdata.unpark(event['Channel'])

    def ami_peerstatus(self, event):
        self.innerdata.updateregistration(event['Peer'], event.get('Address', ''))

    def userevent_user(self, chanprops, event):
        xivo_userid = event.get('XIVO_USERID')
        userprops = self.innerdata.xod_config.get('users').keeplist.get(xivo_userid)
        xivo_srcnum = event.get('XIVO_SRCNUM')
        if userprops is not None:
            usersummary_src = {'fullname': userprops.get('fullname'),
                               'phonenumber': xivo_srcnum}
        else:
            usersummary_src = {'fullname': xivo_srcnum,
                               'phonenumber': xivo_srcnum}

        xivo_lineid = event.get('XIVO_LINEID')
        usersummary_dst = self.innerdata.usersummary_from_phoneid(xivo_lineid)

        chanprops.set_extra_data('xivo', 'desttype', 'user')
        chanprops.set_extra_data('xivo', 'destid', usersummary_dst.get('userid'))
        chanprops.set_extra_data('xivo', 'userid', xivo_userid)
        chanprops.set_extra_data('xivo', 'origin', 'internal')
        chanprops.set_extra_data('xivo', 'direction', 'internal')
        chanprops.set_extra_data('xivo', 'calleridnum', usersummary_src.get('phonenumber'))
        chanprops.set_extra_data('xivo', 'calleridname', usersummary_src.get('fullname'))
        chanprops.set_extra_data('xivo', 'calledidnum', usersummary_dst.get('phonenumber'))
        chanprops.set_extra_data('xivo', 'calledidname', usersummary_dst.get('fullname'))

    def userevent_group(self, chanprops, event):
        xivo_userid = event.get('XIVO_USERID')
        chanprops.set_extra_data('xivo', 'userid', xivo_userid)

    def userevent_queue(self, chanprops, event):
        xivo_userid = event.get('XIVO_USERID')
        chanprops.set_extra_data('xivo', 'userid', xivo_userid)

    def userevent_meetme(self, chanprops, event):
        xivo_userid = event.get('XIVO_USERID')
        chanprops.set_extra_data('xivo', 'userid', xivo_userid)

    def userevent_outcall(self, chanprops, event):
        xivo_userid = event.get('XIVO_USERID')
        chanprops.set_extra_data('xivo', 'userid', xivo_userid)
        chanprops.set_extra_data('xivo', 'origin', 'outcall')
        chanprops.set_extra_data('xivo', 'direction', 'outgoing')
        self.innerdata.sheetsend('outcall', chanprops.channel)

    def userevent_did(self, chanprops, event):
        calleridnum = event.get('XIVO_SRCNUM')
        calleridname = event.get('XIVO_SRCNAME')
        calleridton = event.get('XIVO_SRCTON')
        calleridrdnis = event.get('XIVO_SRCRDNIS')
        didnumber = event.get('XIVO_EXTENPATTERN')

        chanprops.set_extra_data('xivo', 'origin', 'did')
        chanprops.set_extra_data('xivo', 'direction', 'incoming')
        chanprops.set_extra_data('xivo', 'did', didnumber)
        chanprops.set_extra_data('xivo', 'calleridnum', calleridnum)
        chanprops.set_extra_data('xivo', 'calleridname', calleridname)
        chanprops.set_extra_data('xivo', 'calleridrdnis', calleridrdnis)
        chanprops.set_extra_data('xivo', 'calleridton', calleridton)
        for incall_config in self.innerdata.xod_config.get('incalls').keeplist.itervalues():
            if incall_config.get('exten') == didnumber:
                for incall_property, incall_value in incall_config.iteritems():
                    if incall_property != 'context' and incall_property.endswith('context') and incall_value:
                        chanprops.set_extra_data('xivo', 'context', incall_value)
        self.innerdata.sheetsend('incomingdid', chanprops.channel)

    def userevent_lookupdirectory(self, chanprops, event):
        calleridnum = event.get('XIVO_SRCNUM')
        calleridname = event.get('XIVO_SRCNAME')
        calleridton = event.get('XIVO_SRCTON')
        calleridrdnis = event.get('XIVO_SRCRDNIS')
        context = event.get('XIVO_CONTEXT')

        chanprops.set_extra_data('xivo', 'origin', 'forcelookup')
        chanprops.set_extra_data('xivo', 'context', context)
        chanprops.set_extra_data('xivo', 'calleridnum', calleridnum)
        chanprops.set_extra_data('xivo', 'calleridname', calleridname)
        chanprops.set_extra_data('xivo', 'calleridrdnis', calleridrdnis)
        chanprops.set_extra_data('xivo', 'calleridton', calleridton)
        # directory lookup : update chanprops

    def userevent_feature(self, chanprops, ev):
        reply = {}
        if 'XIVO_USERID' in ev and 'Function' in ev and 'Status' in ev:
            userid = ev['XIVO_USERID']
            status = int(ev['Status']) != 0
            user = self.innerdata.xod_config['users'].keeplist[userid]
            fn = ev['Function']
            if 'dnd' in fn:
                user['enablednd'] = status
            if 'callrecord' in fn:
                user['callrecord'] = status
            if 'incallfilter' in fn:
                user['incallfilter'] = status
            if 'unc' == fn:
                fn = 'enableunc'
                user[fn] = status
                user['destunc'] = ev.get('Value')
            if 'rna' == fn:
                fn = 'enablerna'
                user[fn] = status
                user['destrna'] = ev.get('Value')
            if 'busy' == fn:
                fn = 'enablebusy'
                user[fn] = status
                user['destbusy'] = ev.get('Value')
            event = {'class': 'getlist',
                     'listname': 'users',
                     'function': 'updateconfig',
                     'tipbxid': self.ipbxid,
                     'tid': userid,
                     'config': user}
            self.innerdata.events_cti.put(event)
        return reply

    def userevent_dialplan2cti(self, chanprops, event):
        # why "UserEvent + dialplan2cti" and not "Newexten + Set" ?
        # - more selective
        # - variables declarations are not always done with Set (Read(), AGI(), ...)
        # - if there is a need for extra useful data (XIVO_USERID, ...)
        # - (future ?) multiple settings at once
        cti_varname = event.get('VARIABLE')
        dp_value = event.get('VALUE')
        chanprops.set_extra_data('dp', cti_varname, dp_value)

    def ami_userevent(self, event):
        eventname = event['UserEvent']
        channel = event.get('CHANNEL')
        # syntax in dialplan : exten = xx,n,UserEvent(myevent,var1: ${var1},var2: ${var2})
        if channel in self.innerdata.channels:
            if eventname in self.userevents:
                methodname = 'userevent_%s' % eventname.lower()
                if hasattr(self, methodname):
                    chanprops = self.innerdata.channels[channel]
                    getattr(self, methodname)(chanprops, event)

    def handle_fagi(self, fastagi):
        return

    def ami_messagewaiting(self, event):
        try:
            full_mailbox = event['Mailbox']
            for mailbox_id, mailbox in self.innerdata.xod_config['voicemails'].keeplist.iteritems():
                if full_mailbox == mailbox['fullmailbox']:
                    previous_status = self.innerdata.xod_status['voicemails'][mailbox_id]
                    old = event.get('Old') or previous_status['old']
                    new = event.get('New') or previous_status['new']
                    waiting = event.get('Waiting') or previous_status['waiting']
                    self.innerdata.voicemailupdate(full_mailbox, new, old, waiting)
            if 'Old' not in event and 'New' not in event:
                params = {'mode': 'vmupdate',
                          'amicommand': 'mailboxcount',
                          'amiargs': full_mailbox.split('@')}
                actionid = ''.join(random.sample(ALPHANUMS, 10))
                self._ctiserver.myami.get(self.ipbxid).execute_and_track(actionid, params)
        except KeyError:
            logger.warning('ami_messagewaiting Failed to update mailbox')

    def ami_meetmelist(self, event):
        opts = {'usernum': event['UserNumber'],
                'admin': 'Yes' in event['Admin'],
                'muted': 'No' not in event['Muted'],
                'displayname': event['CallerIDName'],
                'phonenumber': event['CallerIDNum']}
        return self.innerdata.meetmeupdate(event['Conference'],
                                           event['Channel'], opts)

    def ami_coreshowchannel(self, event):
        channel = event['Channel']
        context = event['Context']
        application = event['Application']
        bridgedchannel = event['BridgedChannel']
        state = event['ChannelState']
        timestamp_start = self.timeconvert(event['Duration'])

        self.innerdata.newchannel(channel, context, state)
        channelstruct = self.innerdata.channels[channel]

        channelstruct.properties['timestamp'] = timestamp_start
        if application == 'Dial':
            channelstruct.properties['direction'] = 'out'
            if state == '6':
                channelstruct.properties['commstatus'] = 'linked-caller'
            elif state == '4':
                channelstruct.properties['commstatus'] = 'calling'
        elif application == 'AppDial':
            channelstruct.properties['direction'] = 'in'
            if state == '6':
                channelstruct.properties['commstatus'] = 'linked-called'
            elif state == '5':
                channelstruct.properties['commstatus'] = 'ringing'

        if state == '6' and bridgedchannel:
            self.innerdata.newchannel(bridgedchannel, context, state)
            self.innerdata.setpeerchannel(channel, bridgedchannel)
            self.innerdata.setpeerchannel(bridgedchannel, channel)

    def ami_listdialplan(self, event):
        extension = event.get('Extension')
        if extension and extension.isdigit() and event['Priority'] == '1':
            actionid = 'exten:%s' % ''.join(random.sample(ALPHANUMS, 10))
            params = {'mode': 'extension',
                      'amicommand': 'sendextensionstate',
                      'amiargs': (extension, event['Context'])}
            self._ctiserver.myami.get(self.ipbxid).execute_and_track(actionid, params)

    def ami_voicemailuserentry(self, event):
        fullmailbox = '%s@%s' % (event['VoiceMailbox'], event['VMContext'])
        # only NewMessageCount here - OldMessageCount only when IMAP compiled
        # relation to Old/New/Waiting in MessageWaiting UserEvent ?
        self.innerdata.voicemailupdate(fullmailbox, event['NewMessageCount'])

    def ami_monitorstart(self, event):
        channel = event['Channel']
        if channel in self.innerdata.channels:
            self.innerdata.channels.get(channel).properties['monitored'] = True

    def ami_monitorstop(self, event):
        channel = event['Channel']
        if channel in self.innerdata.channels:
            self.innerdata.channels.get(channel).properties['monitored'] = False

    def amiresponse_extensionstatus(self, event):
        if 'Hint' in event:
            self.innerdata.updatehint(event['Hint'], event['Status'])

    @staticmethod
    def timeconvert(duration):
        if duration.find(':') >= 0:
            # like in core show channels output
            vdur = duration.split(':')
            duration_secs = int(vdur[0]) * 3600 + int(vdur[1]) * 60 + int(vdur[2])
        else:
            # like in queue entry output
            duration_secs = int(duration)
        timestamp_start = time.time() - duration_secs
        return timestamp_start
