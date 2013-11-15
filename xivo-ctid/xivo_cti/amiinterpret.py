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
import random
import string
import time

from xivo_cti.call_forms.variable_aggregator import CallFormVariable as Var
from xivo_dao import group_dao
from xivo_dao import incall_dao
from xivo_dao import user_dao
from xivo_dao import queue_dao

ALPHANUMS = string.uppercase + string.lowercase + string.digits

logger = logging.getLogger('AMI_1.8')


class AMI_1_8(object):

    userevents = ('Feature',
                  'dialplan2cti',
                  'User',
                  'Queue',
                  'Group',
                  'Did')

    def __init__(self, cti_server, innerdata, interface_ami, call_form_dispatch_filter, call_form_variable_aggregator):
        self._ctiserver = cti_server
        self.innerdata = innerdata
        self.interface_ami = interface_ami
        self._call_form_dispatch_filter = call_form_dispatch_filter
        self._aggregator = call_form_variable_aggregator

    def ami_newchannel(self, event):
        channel = event['Channel']
        state = event['ChannelState']
        state_description = event['ChannelStateDesc']
        context = event['Context']
        unique_id = event['Uniqueid']

        _set = self._get_set_fn(unique_id)
        _set('calleridname', event['CallerIDName'])
        _set('calleridnum', event['CallerIDNum'])
        _set('channel', event['Channel'])
        _set('context', context)

        self.innerdata.newchannel(channel, context, state, state_description, unique_id)

    def ami_hangup(self, event):
        channel = event['Channel']
        uniqueid = event['Uniqueid']

        self._call_form_dispatch_filter.handle_hangup(uniqueid, channel)
        self.innerdata.hangup(channel)
        self._aggregator.clean(uniqueid)

    def ami_dial(self, event):
        channel = event['Channel']
        subevent = event['SubEvent']
        uniqueid = event['UniqueID']
        _set = self._get_set_fn(uniqueid)
        if subevent == 'Begin' and 'Destination' in event:
            destination = event['Destination']
            if channel in self.innerdata.channels:
                try:
                    _set('desttype', 'user')
                    phone = self.innerdata.xod_config['phones'].find_phone_by_channel(destination)
                    if phone:
                        _set('destid', str(phone['iduserfeatures']))
                except LookupError:
                    logger.exception('Could not set user id for dial')
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
            self._call_form_dispatch_filter.handle_dial(uniqueid, channel)

    def ami_extensionstatus(self, event):
        self.innerdata.updatehint(event['Hint'], event['Status'])

    def ami_bridge(self, event):
        if event['Bridgestate'] != 'Link':
            return

        channel_1 = self.innerdata.channels.get(event['Channel1'])
        channel_2 = self.innerdata.channels.get(event['Channel2'])
        uniqueid = event['Uniqueid1']
        channel_name = event['Channel1']

        if channel_1:
            self._update_connected_channel(channel_1, channel_2)
            channel_1.properties['commstatus'] = 'linked-caller'

        if channel_2:
            self._update_connected_channel(channel_2, channel_1)
            channel_2.properties['commstatus'] = 'linked-called'

        self._call_form_dispatch_filter.handle_bridge(uniqueid, channel_name)

    def _update_connected_channel(self, channel, peer_channel):
        channel.properties.update({
            'talkingto_kind': 'channel',
            'talkingto_id': peer_channel.channel,
            'timestamp': time.time(),
        })
        self.innerdata.setpeerchannel(channel.channel, peer_channel.channel)
        self.innerdata.update(channel.channel)

    def ami_masquerade(self, event):
        original = event['Original']
        clone = event['Clone']
        self.innerdata.masquerade(original, clone)

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
        if actionid in self.interface_ami.originate_actionids:
            properties = self.interface_ami.originate_actionids.pop(actionid)
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

    def ami_parkedcall(self, event):
        channel = event['Channel']
        exten = event['Exten']
        parkinglot = event['Parkinglot']
        if parkinglot.startswith('parkinglot_'):
            parkinglot = '_'.join(parkinglot.split('_')[1:])
        if channel in self.innerdata.channels:
            self.innerdata.channels[channel].setparking(exten, parkinglot)

    def ami_unparkedcall(self, event):
        channel = event['Channel']
        if channel in self.innerdata.channels:
            self.innerdata.channels[channel].unsetparking()

    def ami_parkedcalltimeout(self, event):
        channel = event['Channel']
        if channel in self.innerdata.channels:
            self.innerdata.channels[channel].unsetparking()

    def userevent_user(self, chanprops, event):
        uniqueid = event['Uniqueid']
        _set = self._get_set_fn(uniqueid)
        xivo_userid = event.get('XIVO_USERID')
        destination_user_id = int(event['XIVO_DSTID'])
        channel_name = event['CHANNEL']
        destination_name, destination_number = user_dao.get_name_number(destination_user_id)

        _set('desttype', 'user')
        _set('destid', destination_user_id)
        _set('userid', xivo_userid)
        _set('origin', event.get('XIVO_CALLORIGIN', 'internal'))
        _set('direction', 'internal')
        _set('calledidnum', destination_number)
        _set('calledidname', destination_name)
        self._call_form_dispatch_filter.handle_user(uniqueid, channel_name)

    def userevent_queue(self, chanprops, event):
        uniqueid = event['Uniqueid']
        _set = self._get_set_fn(uniqueid)
        queue_id = int(event['XIVO_DSTID'])
        channel_name = event['CHANNEL']
        queue_name, queue_number = queue_dao.get_display_name_number(queue_id)

        _set('desttype', 'queue')
        _set('destid', queue_id)
        _set('calledidname', queue_name)
        _set('queuename', queue_name)
        _set('calledidnum', queue_number)

        self._call_form_dispatch_filter.handle_queue(uniqueid, channel_name)

    def userevent_group(self, chanprops, event):
        uniqueid = event['Uniqueid']
        _set = self._get_set_fn(uniqueid)
        group_id = int(event['XIVO_DSTID'])
        channel_name = event['CHANNEL']
        group_name, group_number = group_dao.get_name_number(group_id)

        _set('desttype', 'group')
        _set('destid', group_id)
        _set('calledidname', group_name)
        _set('calledidnum', group_number)

        self._call_form_dispatch_filter.handle_group(uniqueid, channel_name)

    def userevent_did(self, chanprops, event):
        uniqueid = event['Uniqueid']
        _set = self._get_set_fn(uniqueid)
        calleridnum = event.get('XIVO_SRCNUM')
        calleridname = event.get('XIVO_SRCNAME')
        calleridton = event.get('XIVO_SRCTON')
        calleridrdnis = event.get('XIVO_SRCRDNIS')
        didnumber = event.get('XIVO_EXTENPATTERN')

        _set('origin', 'did')
        _set('direction', 'incoming')
        _set('did', didnumber)
        _set('calleridnum', calleridnum)
        _set('calleridname', calleridname)
        _set('calleridrdnis', calleridrdnis)
        _set('calleridton', calleridton)
        _set('channel', chanprops.channel)
        incall = incall_dao.get_by_exten(didnumber)
        if incall:
            _set('desttype', incall.action)
            _set('destid', incall.actionarg1)
        self._call_form_dispatch_filter.handle_did(uniqueid, chanprops.channel)

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
                     'tipbxid': self._ctiserver.myipbxid,
                     'tid': userid,
                     'config': user}
            self._ctiserver.send_cti_event(event)
        return reply

    def userevent_dialplan2cti(self, chanprops, event):
        # why "UserEvent + dialplan2cti" and not "Newexten + Set" ?
        # - more selective
        # - variables declarations are not always done with Set (Read(), AGI(), ...)
        # - if there is a need for extra useful data (XIVO_USERID, ...)
        # - (future ?) multiple settings at once
        uniqueid = event['Uniqueid']
        cti_varname = event.get('VARIABLE')
        dp_value = event.get('VALUE')
        self._aggregator.set(uniqueid, Var('dp', cti_varname, dp_value))

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

    def ami_messagewaiting(self, event):
        try:
            full_mailbox = event['Mailbox']
            for mailbox_id, mailbox in self.innerdata.xod_config['voicemails'].keeplist.iteritems():
                if full_mailbox == mailbox['fullmailbox']:
                    previous_status = self.innerdata.xod_status['voicemails'][mailbox_id]
                    old = event.get('Old') or previous_status['old']
                    new = event.get('New') or previous_status['new']
                    waiting = event.get('Waiting') or previous_status['waiting']
                    logger.info("Voicemail event received. mailbox:%s new:%s old:%s waiting:%s", full_mailbox, new, old, waiting)
                    self.innerdata.voicemailupdate(full_mailbox, new, old, waiting)
            if 'Old' not in event and 'New' not in event:
                logger.info("Voicemail event did not contain 'old' and 'new' count. retrieving mailbox count")
                params = {'mode': 'vmupdate',
                          'amicommand': 'mailboxcount',
                          'amiargs': full_mailbox.split('@')}
                actionid = ''.join(random.sample(ALPHANUMS, 10))
                self.interface_ami.execute_and_track(actionid, params)
        except KeyError:
            logger.warning('ami_messagewaiting Failed to update mailbox')

    def ami_coreshowchannel(self, event):
        channel = event['Channel']
        context = event['Context']
        application = event['Application']
        bridgedchannel = event['BridgedChannel']
        state = event['ChannelState']
        state_description = event['ChannelStateDesc']
        timestamp_start = self.timeconvert(event['Duration'])
        unique_id = event['UniqueID']

        self.innerdata.newchannel(channel, context, state, state_description, unique_id)
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
            self.innerdata.newchannel(bridgedchannel, context, state, state_description, unique_id)
            self.innerdata.setpeerchannel(channel, bridgedchannel)
            self.innerdata.setpeerchannel(bridgedchannel, channel)

    def ami_listdialplan(self, event):
        extension = event.get('Extension')
        if extension and extension.isdigit() and event['Priority'] == '1':
            actionid = 'exten:%s' % ''.join(random.sample(ALPHANUMS, 10))
            params = {'mode': 'extension',
                      'amicommand': 'sendextensionstate',
                      'amiargs': (extension, event['Context'])}
            self.interface_ami.execute_and_track(actionid, params)

    def ami_voicemailuserentry(self, event):
        fullmailbox = '%s@%s' % (event['VoiceMailbox'], event['VMContext'])
        # only NewMessageCount here - OldMessageCount only when IMAP compiled
        # relation to Old/New/Waiting in MessageWaiting UserEvent ?
        self.innerdata.voicemailupdate(fullmailbox, event['NewMessageCount'])

    def amiresponse_extensionstatus(self, event):
        hint = event.get('Hint')
        if hint:
            self.innerdata.updatehint(hint, event['Status'])

    def _get_set_fn(self, uniqueid):
        def _set(var_name, var_value):
            self._aggregator.set(uniqueid, Var('xivo', var_name, var_value))
        return _set

    @staticmethod
    def timeconvert(duration):
        if ':' in duration:
            # like in core show channels output
            vdur = duration.split(':')
            duration_secs = int(vdur[0]) * 3600 + int(vdur[1]) * 60 + int(vdur[2])
        else:
            # like in queue entry output
            duration_secs = int(duration)
        timestamp_start = time.time() - duration_secs
        return timestamp_start
