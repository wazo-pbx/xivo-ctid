# -*- coding: utf-8 -*-
# Copyright (C) 2007-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging
import random
import time

from xivo_cti import ALPHANUMS
from xivo_cti.call_forms.variable_aggregator import CallFormVariable as Var
from xivo_cti.channel import ChannelRole
from xivo_cti.database import user_db

from xivo_dao.helpers.db_utils import session_scope

from xivo_dao import group_dao
from xivo_dao import incall_dao
from xivo_dao import queue_dao

logger = logging.getLogger('AMI_1.8')


class AMI_1_8(object):

    userevents = ('dialplan2cti',
                  'User',
                  'Queue',
                  'Group',
                  'Did',
                  'FaxProgress')

    def __init__(self, cti_server, innerdata, interface_ami,
                 call_form_dispatch_filter, call_form_variable_aggregator,
                 endpoint_status_updater):
        self._ctiserver = cti_server
        self.innerdata = innerdata
        self.interface_ami = interface_ami
        self._call_form_dispatch_filter = call_form_dispatch_filter
        self._aggregator = call_form_variable_aggregator
        self._endpoint_status_updater = endpoint_status_updater

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
        self._aggregator.on_hangup(uniqueid)

    def ami_dialbegin(self, event):
        channel = event.get('Channel')
        if channel is None:
            # If there are no channel, it's a dial initiated by an Originate
            return
        uniqueid = event['Uniqueid']
        _set = self._get_set_fn(uniqueid)
        destination = event['DestChannel']
        if channel in self.innerdata.channels:
            try:
                _set('desttype', 'user')
                phone = self.innerdata.xod_config['phones'].find_phone_by_channel(destination)
                if phone:
                    _set('destid', str(phone['iduserfeatures']))
            except LookupError:
                logger.exception('Could not set user id for dial')
            self.innerdata.channels[channel].role = ChannelRole.caller
        if destination in self.innerdata.channels:
            self.innerdata.channels[destination].role = ChannelRole.callee
        self._call_form_dispatch_filter.handle_dial(uniqueid, channel)

    def ami_extensionstatus(self, event):
        self._endpoint_status_updater.update_status(event['Hint'], event['Status'])

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

    def userevent_user(self, chanprops, event):
        uniqueid = event['Uniqueid']
        _set = self._get_set_fn(uniqueid)
        xivo_userid = event.get('XIVO_USERID')
        destination_user_id = int(event['XIVO_DSTID'])
        channel_name = event['CHANNEL']

        destination_name, destination_number = user_db.get_name_number(destination_user_id)

        _set('desttype', 'user')
        _set('destid', destination_user_id)
        _set('userid', xivo_userid)
        _set('origin', event.get('XIVO_CALLORIGIN', 'internal'))
        _set('direction', 'internal')
        _set('calledidnum', destination_number)
        _set('calledidname', destination_name)
        self._call_form_dispatch_filter.handle_user(uniqueid, channel_name)

    def userevent_queue(self, chanprops, event):
        # This function does not trigger a "sheet send"; it is only used to update the
        # internal variables available on further sheet send (i.e. on link and unlink events)
        uniqueid = event['Uniqueid']
        _set = self._get_set_fn(uniqueid)
        queue_id = int(event['XIVO_DSTID'])

        with session_scope():
            queue_name, queue_number = queue_dao.get_display_name_number(queue_id)

        _set('calledidname', queue_name)
        _set('queuename', queue_name)
        _set('calledidnum', queue_number)

    def userevent_group(self, chanprops, event):
        # This function does not trigger a "sheet send"; it is only used to update the
        # internal variables available on further sheet send (i.e. on link and unlink events)
        uniqueid = event['Uniqueid']
        _set = self._get_set_fn(uniqueid)
        group_id = int(event['XIVO_DSTID'])

        with session_scope():
            group_name, group_number = group_dao.get_name_number(group_id)

        _set('calledidname', group_name)
        _set('calledidnum', group_number)

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

        with session_scope():
            incall = incall_dao.get_by_exten(didnumber)

        if incall:
            _set('desttype', incall.action)
            _set('destid', incall.actionarg1)
        self._call_form_dispatch_filter.handle_did(uniqueid, chanprops.channel)

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

    def userevent_faxprogress(self, chanprops, event):
        userid = event['XIVO_USERID']
        status = event['STATUS']
        pages = event.get('PAGES')
        event = {'class': 'fax_progress',
                 'status': status,
                 'pages': pages}
        userxid = '{ipbxid}/{userid}'.format(ipbxid='xivo', userid=userid)
        self._ctiserver.send_to_cti_client(userxid, event)

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
        mailbox_id = self._voicemail_id_from_fullmailbox(event['Mailbox'])
        if mailbox_id:
            self.innerdata.voicemailupdate(mailbox_id, event['New'])

    def ami_coreshowchannel(self, event):
        channel = event['Channel']
        context = event['Context']
        state = event['ChannelState']
        state_description = event['ChannelStateDesc']
        unique_id = event['Uniqueid']

        self.innerdata.newchannel(channel, context, state, state_description, unique_id)

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
        voicemail_id = self._voicemail_id_from_fullmailbox(fullmailbox)
        if voicemail_id:
            self.innerdata.voicemailupdate(voicemail_id, event['NewMessageCount'])

    def amiresponse_extensionstatus(self, event):
        hint = event.get('Hint')
        if hint:
            self._endpoint_status_updater.update_status(hint, event['Status'])

    def _voicemail_id_from_fullmailbox(self, fullmailbox):
        for voicemail_id, vm_config in self.innerdata.xod_config['voicemails'].keeplist.iteritems():
            if vm_config['fullmailbox'] == fullmailbox:
                return voicemail_id
        return None

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
