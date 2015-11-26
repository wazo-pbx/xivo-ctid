# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

import copy
import hashlib
import logging
import time

from contextlib import contextmanager

from datetime import timedelta
from xivo_auth_client import Client as AuthClient
from xivo_cti import cti_sheets
from xivo_cti import config
from xivo_cti.ami import ami_callback_handler
from xivo_cti.call_forms.variable_aggregator import CallFormVariable
from xivo_cti.channel import Channel
from xivo_cti.cti.commands.getlist import ListID, UpdateConfig, UpdateStatus
from xivo_cti.cti.commands.availstate import Availstate
from xivo_cti.cti_daolist import NotFoundError
from xivo_cti.ioc.context import context
from xivo_cti.lists import (agents_list, groups_list, meetmes_list,
                            phones_list, queues_list, users_list, voicemails_list,
                            trunks_list)

from xivo_dao.helpers.db_utils import session_scope
from xivo_dao import group_dao
from xivo_dao import queue_dao
from xivo_dao import trunk_dao
from xivo_dao.resources.user import dao as user_dao

from collections import defaultdict

logger = logging.getLogger('innerdata')

TWO_MONTHS = timedelta(days=60).total_seconds()


@contextmanager
def auth_client(userid):
    with session_scope():
        user = user_dao.get(userid)
        username = user.username
        password = user.password

    yield AuthClient(username=username, password=password, **config['auth'])


class Safe(object):

    def __init__(self, cti_server, queue_member_cti_adapter):
        self._ctiserver = cti_server
        self.queue_member_cti_adapter = queue_member_cti_adapter
        self.ipbxid = 'xivo'
        self.xod_config = {}
        self.xod_status = {}
        self.channels = {}
        self.faxes = {}
        self.ctistack = []
        self._sent_sheets = defaultdict(list)

    def init_xod_config(self):
        self.xod_config = {
            'agents': agents_list.AgentsList(self),
            'groups': groups_list.GroupsList(self),
            'meetmes': meetmes_list.MeetmesList(self),
            'phones': phones_list.PhonesList(self),
            'queues': queues_list.QueuesList(self),
            'trunks': trunks_list.TrunksList(self),
            'users': users_list.UsersList(self),
            'voicemails': voicemails_list.VoicemailsList(self),
        }

        for config_object in self.xod_config.itervalues():
            config_object.init_data()

    def init_xod_status(self):
        for name, config in self.xod_config.iteritems():
            self.xod_status[name] = config.init_status()

    def update_config_list(self, listname, state, item_id):
        try:
            if state == 'add':
                self._update_config_list_add(listname, item_id)
            elif state in ['edit', 'enable', 'disable']:
                self._update_config_list_change(listname, item_id)
            elif state == 'delete':
                self._update_config_list_del(listname, item_id)
        except NotFoundError:
            logger.info('object %s %s not found', listname, item_id)
        except TypeError:
            logger.warning('id "%s" not set for object %s', item_id, listname)

    def _update_config_list_add(self, listname, item_id):
        self.xod_config[listname].add(item_id)
        self.xod_status[listname][item_id] = self.xod_config[listname].get_status()

    def _update_config_list_del(self, listname, item_id):
        self.xod_config[listname].delete(item_id)
        del self.xod_status[listname][item_id]

    def _update_config_list_change(self, listname, item_id):
        self.xod_config[listname].edit(item_id)

    def get_config(self, listname, item_id, user_contexts=None):
        if listname == 'queuemembers':
            return self.queue_member_cti_adapter.get_config(item_id)
        return self.xod_config[listname].get_item_config(item_id, user_contexts)

    def get_status(self, listname, item_id):
        if listname == 'queuemembers':
            return self.queue_member_cti_adapter.get_status(item_id)

        reply = {}
        statusdict = self.xod_status.get(listname)
        if not isinstance(statusdict, dict):
            logger.warning('get_status : problem with listname %s', listname)
            return reply

        periddict = statusdict.get(item_id)
        if not isinstance(periddict, dict):
            logger.warning('get_status : problem with item_id %s in listname %s',
                           item_id, listname)
            return reply
        return self.xod_config[listname].get_item_status(periddict)

    def register_cti_handlers(self):
        ListID.register_callback_params(self.handle_getlist_list_id, ['list_name', 'user_id'])
        UpdateConfig.register_callback_params(self.handle_getlist_update_config, ['user_id', 'list_name', 'item_id'])
        UpdateStatus.register_callback_params(self.handle_getlist_update_status, ['list_name', 'item_id'])
        Availstate.register_callback_params(self.user_service_manager.set_presence, ['user_id', 'availstate'])

    def register_ami_handlers(self):
        ami_handler = ami_callback_handler.AMICallbackHandler.get_instance()
        ami_handler.register_callback('AgentCalled', self.handle_agent_called)
        ami_handler.register_callback('AgentConnect', self.handle_agent_linked)
        ami_handler.register_callback('AgentComplete', self.handle_agent_unlinked)
        ami_handler.register_userevent_callback('AgentLogin', self.handle_agent_login)

    def _set_channel_extra_vars_agent(self, event, member_name):
        uniqueid = event['Uniqueid']
        _set = self._get_set_fn(uniqueid)
        proto, agent_number = member_name.split('/', 1)
        try:
            if proto == 'Agent':
                _set('agentnumber', agent_number)
                data_type = 'agent'
                data_id = self.xod_config['agents'].idbyagentnumber(agent_number)
            else:
                data_type = 'user'
                phone_id = self.zphones(proto, agent_number)
                if not phone_id:
                    return
                with session_scope():
                    user = user_dao.get_main_user_by_line_id(phone_id)
                    data_id = str(user.id)
            _set('desttype', data_type)
            _set('destid', data_id)
        except NotFoundError:
            raise
        except (AttributeError, LookupError) as e:
            logger.exception(e)
            logger.warning('Failed to set agent channel variables for event: %s', event)

    def handle_agent_called(self, event):
        member_name = event['MemberName']
        uniqueid = event['Uniqueid']
        self._set_channel_extra_vars_agent(event, member_name)
        context.get('call_form_dispatch_filter').handle_agent_called(uniqueid)

    def handle_agent_linked(self, event):
        member_name = event['MemberName']
        uniqueid = event['Uniqueid']
        self._set_channel_extra_vars_agent(event, member_name)
        context.get('call_form_dispatch_filter').handle_agent_connect(uniqueid)
        context.get('call_form_variable_aggregator').on_agent_connect(uniqueid)

    def handle_agent_unlinked(self, event):
        member_name = event['MemberName']
        uniqueid = event['Uniqueid']
        self._set_channel_extra_vars_agent(event, member_name)
        context.get('call_form_dispatch_filter').handle_agent_complete(uniqueid)
        context.get('call_form_variable_aggregator').on_agent_complete(uniqueid)

    def handle_agent_login(self, event):
        agent_id = event['AgentID']
        self.handle_cti_stack('set', ('agents', 'updatestatus', agent_id))
        agstatus = self.xod_status['agents'].get(agent_id)
        agstatus['phonenumber'] = event['Extension']
        self.handle_cti_stack('empty_stack')

    def handle_getlist_list_id(self, listname, user_id):
        if listname in self.xod_config or listname == 'queuemembers':
            if listname in self.xod_config:
                user_contexts = self.xod_config['users'].get_contexts(user_id)
                item_ids = self.xod_config[listname].list_ids_in_contexts(user_contexts)
            elif listname == 'queuemembers':
                item_ids = self.queue_member_cti_adapter.get_list()
            return 'message', {'function': 'listid',
                               'listname': listname,
                               'tipbxid': self.ipbxid,
                               'list': item_ids,
                               'class': 'getlist'}
        else:
            logger.debug('no such list %s', listname)

    def handle_getlist_update_config(self, user_id, list_name, item_id):
        user_contexts = self.xod_config['users'].get_contexts(user_id)
        item = self.get_config(list_name, item_id, user_contexts=user_contexts)
        return 'message', {'function': 'updateconfig',
                           'listname': list_name,
                           'tipbxid': self.ipbxid,
                           'tid': item_id,
                           'class': 'getlist',
                           'config': item}

    def handle_getlist_update_status(self, list_name, item_id):
        item = self.get_status(list_name, item_id)
        return 'message', {'function': 'updatestatus',
                           'listname': list_name,
                           'tipbxid': self.ipbxid,
                           'tid': item_id,
                           'class': 'getlist',
                           'status': item}

    def user_match(self, userid, tomatch):
        domatch = False
        user = self.xod_config['users'].keeplist.get(userid)
        if not user:
            return False

        # does the user fullfil the destination criteria ?
        if 'desttype' in tomatch and 'destid' in tomatch:
            dest_type, dest_id = tomatch['desttype'], tomatch['destid']
            if dest_type == 'user' and userid == str(dest_id):
                domatch = True
            elif dest_type == 'agent':
                domatch = user['agentid'] == int(dest_id)
            elif dest_type == 'queue' and dest_id:
                with session_scope():
                    domatch = queue_dao.is_user_member_of_queue(userid, dest_id)
            elif dest_type == 'group' and dest_id:
                with session_scope():
                    domatch = group_dao.is_user_member_of_group(userid, dest_id)
        else:
            # 'all' case
            domatch = True

        if domatch and 'profileids' in tomatch:
            if user['cti_profile_id'] not in tomatch['profileids']:
                domatch = False

        if domatch and 'contexts' in tomatch:
            domatch = False
            if user['context'] in tomatch['contexts']:
                domatch = True

        return domatch

    def user_get_hashed_password(self, userid, sessionid):
        with session_scope():
            password = user_dao.get(userid).password
        tohash = '%s:%s' % (sessionid, password)
        sha1sum = hashlib.sha1(tohash).hexdigest()
        return sha1sum

    def user_new_auth_token(self, userid):
        with auth_client(userid) as client:
            return client.token.new('xivo_user', expiration=TWO_MONTHS)['token']

    def user_remove_auth_token(self, userid, token):
        with auth_client(userid) as client:
            client.token.revoke(token)

    def newchannel(self, channel_name, context, state, state_description, unique_id):
        if not channel_name:
            return
        if channel_name not in self.channels:
            channel = Channel(channel_name, context, unique_id)
            self.channels[channel_name] = channel
        self.updaterelations(channel_name)

    def voicemailupdate(self, mailbox, new, old=None, waiting=None):
        for k, v in self.xod_config['voicemails'].keeplist.iteritems():
            if mailbox == v.get('fullmailbox'):
                self.handle_cti_stack('set', ('voicemails', 'updatestatus', k))
                self.xod_status['voicemails'][k].update({'old': old,
                                                         'new': new,
                                                         'waiting': waiting})
                self.handle_cti_stack('empty_stack')
                logger.info("voicemail %s updated. new:%s old:%s waiting:%s", mailbox, new, old, waiting)
                break

    def update(self, channel):
        chanprops = self.channels.get(channel)
        relations = chanprops.relations
        for r in relations:
            if r.startswith('phone:'):
                self.handle_cti_stack('setforce', ('phones', 'updatestatus', r[6:]))
        self.handle_cti_stack('empty_stack')

    def statusbylist(self, listname, item_id):
        if listname == 'queuemembers':
            return self.queue_member_cti_adapter.get_status(item_id)
        else:
            if item_id and item_id in self.xod_status[listname]:
                return self.xod_status[listname].get(item_id)

    def appendcti(self, listname, which, item_id, status=None):
        if not status and int(item_id) > 0:
            status = self.statusbylist(listname, item_id)

        if status:
            evt = {'class': 'getlist',
                   'listname': listname,
                   'function': which,
                   'tipbxid': self.ipbxid,
                   'tid': item_id,
                   'status': status}
            self._ctiserver.send_cti_event(evt)

    def handle_cti_stack(self, action, event=None):
        """
        The idea behind this method is to fill a list of would-be cti events
        with 'set', retrieve the statuses at this point.
        Later on, with 'empty_stack', one might compare whether and how the statuses
        have changed and send them accordingly ...
        'setforce' empties the first status, in order for the event to be always sent.
        """
        if action == 'set':
            (listname, _, item) = event
            thisstatus = copy.deepcopy(self.statusbylist(listname, item))
            self.ctistack.append((event, thisstatus))
        elif action == 'setforce':
            self.ctistack.append((event, {}))
        elif action == 'empty_stack':
            while self.ctistack:
                (oldevent, oldstatus) = self.ctistack.pop()
                (listname, _, item) = oldevent
                newstatus = self.statusbylist(listname, item)
                if oldstatus != newstatus:
                    if oldstatus is None:
                        sendstatus = newstatus
                    else:
                        sendstatus = {}
                        for k, v in newstatus.iteritems():
                            if v != oldstatus.get(k):
                                sendstatus[k] = v
                    oldevent_list = list(oldevent)
                    oldevent_list.append(sendstatus)
                    self.appendcti(* oldevent_list)

    def hangup(self, channel):
        if channel in self.channels:
            self._remove_channel_relations(channel)
            del self.channels[channel]

    def _remove_channel_relations(self, channel):
        relations = self.channels[channel].relations
        for r in relations:
            termination_type, termination_id = r.split(':', 1)
            list_name = termination_type + 's'
            if list_name == 'trunks':
                termination_id = int(termination_id)
            chanlist = self.xod_status[list_name][termination_id]['channels']
            if channel in chanlist:
                chanlist.remove(channel)
                if list_name == 'phones':
                    self.appendcti('phones', 'updatestatus', termination_id)

    def updaterelations(self, channel):
        self.channels[channel].relations = []
        if channel.startswith('SIPPeer/'):
            return
        try:
            termination = self.ast_channel_to_termination(channel)
            p = self.zphones(termination.get('protocol'), termination.get('name'))
            if p:
                self.channels[channel].addrelation('phone:%s' % p)
                oldchans = self.xod_status['phones'][p].get('channels')
                if channel not in oldchans:
                    self.handle_cti_stack('set', ('phones', 'updatestatus', p))
                    oldchans.append(channel)
                    self.handle_cti_stack('empty_stack')
                self.xod_status['phones'][p]['channels'] = oldchans
            t = self.ztrunks(termination.get('protocol'), termination.get('name'))
            if t:
                self.channels[channel].addrelation('trunk:%s' % t)
        except LookupError:
            logger.exception('find termination according to channel %s', channel)

    def handle_bridge_link(self, bridge_event):
        channel_1, channel_2 = bridge_event.bridge.channels
        self._update_connected_channel(channel_1, channel_2)
        self._update_connected_channel(channel_2, channel_1)

    def _update_connected_channel(self, channel, peer_channel):
        self.update(channel.channel)

    # IPBX side

    def ast_channel_to_termination(self, channel):
        term = {}
        # special cases : AsyncGoto/IAX2/asteriskisdn-13622<ZOMBIE>
        # SCCP, DAHDI, ...
        # what about a peer called a-b-c ?
        cutchan1 = channel.split('/')
        if len(cutchan1) == 2:
            protocol = cutchan1[0]
            cutchan2 = cutchan1[1].split('-')
            name = cutchan2[0]
            term = {'protocol': protocol, 'name': name}
        return term

    def zphones(self, protocol, name):
        if protocol:
            protocol = protocol.lower()
            return self.xod_config['phones'].get_phone_id_from_proto_and_name(protocol, name)

    def ztrunks(self, protocol, name):
        try:
            with session_scope():
                return trunk_dao.find_by_proto_name(protocol, name)
        except (LookupError, ValueError):
            return None

    def sheetsend(self, where, uid):
        sheets = config.get('sheets')
        if not sheets:
            return

        self.sheetevents = sheets.get('events')
        self.sheetdisplays = sheets.get('displays')
        self.sheetoptions = sheets.get('options')
        self.sheetconditions = sheets.get('conditions')
        if where not in self.sheetevents:
            return

        _set = self._get_set_fn(uid)

        for se in self.sheetevents[where]:
            display_id = se.get('display')
            condition_id = se.get('condition')
            option_id = se.get('option')

            if not self.sheetdisplays.get(display_id):
                continue

            _set('time', time.strftime('%H:%M:%S', time.localtime()))
            _set('date', time.strftime('%Y-%m-%d', time.localtime()))
            _set('where', where)
            _set('uniqueid', uid)
            _set('ipbxid', self.ipbxid)
            channel = context.get('call_form_variable_aggregator').get(uid)['xivo']['channel']
            sheet = cti_sheets.Sheet(where, self.ipbxid, uid)
            sheet.setoptions(self.sheetoptions.get(option_id))
            sheet.setdisplays(self.sheetdisplays.get(display_id))
            sheet.setconditions(self.sheetconditions.get(condition_id))

            # 1. whom / userinfos : according to outdest or destlist to update in Channel structure
            #    + according to conditions
            #    final 'whom' description should be clearly written in order to send across 'any path'
            tomatch = sheet.checkdest()
            tosendlist = self._ctiserver.get_connected(tomatch)

            # 2. make an extra call to a db if requested ? could be done elsewhere (before) also ...

            # 3. build sheet items (according to values)
            sheet.setfields()
            # 4. sheet construct (according to serialization)
            sheet.serialize()
            # 5. sheet manager ?
            # 6. json message / zip or not / b64 / ...
            # print sheet.internaldata

            # 7. send the payload
            self._ctiserver.sendsheettolist(tosendlist,
                                            {'class': 'sheet',
                                             'channel': channel,
                                             'serial': sheet.serial,
                                             'compressed': sheet.compressed,
                                             'payload': sheet.payload})

    def send_fax(self, step, fileid):
        removeme = self.faxes[fileid].step(step)
        if removeme:
            params = self.faxes[fileid].getparams()
            actionid = fileid
            self._ctiserver.interface_ami.execute_and_track(actionid, params)
            del self.faxes[fileid]

    def _get_set_fn(self, uniqueid):
        aggregator = context.get('call_form_variable_aggregator')

        def _set(var_name, var_value):
            aggregator.set(uniqueid, CallFormVariable('xivo', var_name, var_value))

        return _set
