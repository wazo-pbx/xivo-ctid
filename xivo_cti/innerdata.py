# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import copy
import hashlib
import logging
import time

from collections import defaultdict

from xivo_cti import cti_sheets
from xivo_cti import config
from xivo_cti.ami import ami_callback_handler
from xivo_cti.call_forms.variable_aggregator import CallFormVariable
from xivo_cti.channel import Channel
from xivo_cti.cti.commands.getlist import ListID, UpdateConfig, UpdateStatus
from xivo_cti.cti.commands.availstate import Availstate
from xivo_cti.cti_daolist import NotFoundError
from xivo_cti.ioc.context import context
from xivo_cti.lists import (agents_list, meetmes_list, phones_list,
                            queues_list, users_list, voicemails_list)

from xivo_dao.helpers.db_utils import session_scope
from xivo_dao import group_dao
from xivo_dao import queue_dao
from xivo_dao.resources.user import dao as user_dao

logger = logging.getLogger('innerdata')


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
        self.funckey_manager = context.get('funckey_manager')

    def init_xod_config(self):
        self.xod_config = {
            'agents': agents_list.AgentsList(self),
            'meetmes': meetmes_list.MeetmesList(self),
            'phones': phones_list.PhonesList(self),
            'queues': queues_list.QueuesList(self),
            'users': users_list.UsersList(self),
            'voicemails': voicemails_list.VoicemailsList(self),
        }

        for config_object in self.xod_config.itervalues():
            config_object.init_data()

    def init_xod_status(self):
        for name, config in self.xod_config.iteritems():
            self.xod_status[name] = config.init_status()

    def update_config_list(self, listname, state, item_id):
        if listname not in self.xod_config:
            return
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
        if listname == 'users':
            self._update_forwards_blf(item_id)

    def _update_config_list_del(self, listname, item_id):
        self.xod_config[listname].delete(item_id)
        del self.xod_status[listname][item_id]

    def _update_config_list_change(self, listname, item_id):
        self.xod_config[listname].edit(item_id)
        if listname == 'users':
            self._update_forwards_blf(item_id)

    def _update_forwards_blf(self, item_id):
        user = self.xod_config['users'].keeplist[item_id]
        self.funckey_manager.update_all_unconditional_fwd(user['id'], user['enableunc'], user['destunc'])
        self.funckey_manager.update_all_rna_fwd(user['id'], user['enablerna'], user['destrna'])
        self.funckey_manager.update_all_busy_fwd(user['id'], user['enablebusy'], user['destbusy'])

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
        UpdateStatus.register_callback_params(self.handle_getlist_update_status, ['list_name',
                                                                                  'item_id',
                                                                                  'auth_token',
                                                                                  'cti_connection'])
        Availstate.register_callback_params(self.user_service_manager.send_presence, ['auth_token',
                                                                                      'user_uuid',
                                                                                      'availstate'])

    def register_ami_handlers(self):
        ami_handler = ami_callback_handler.AMICallbackHandler.get_instance()
        ami_handler.register_callback('AgentCalled', self.handle_agent_called)
        ami_handler.register_callback('AgentConnect', self.handle_agent_linked)
        ami_handler.register_callback('AgentComplete', self.handle_agent_unlinked)
        ami_handler.register_userevent_callback('AgentLogin', self.handle_agent_login)

    def _set_channel_extra_vars_agent(self, event, member_name):
        uniqueid = event['Uniqueid']
        _set = self._get_set_fn(uniqueid)
        proto, iface = member_name.split('/', 1)
        try:
            if proto == 'Agent':
                _set('agentnumber', iface)
                data_type = 'agent'
                data_id = self.xod_config['agents'].idbyagentnumber(iface)
            else:
                data_type = 'user'
                phone_id = self.xod_config['phones'].get_phone_id_from_proto_and_name(proto.lower(), iface)
                if not phone_id:
                    return
                data_id = self.xod_config['phones'].keeplist[phone_id]['iduserfeatures']
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

    def handle_getlist_update_status(self, list_name, item_id, auth_token, cti_connection):
        if list_name == 'users':
            self.user_service_manager.get_presence(auth_token, item_id, cti_connection)
            return

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

    def newchannel(self, channel_name, context, state, state_description, unique_id):
        if not channel_name:
            return
        if channel_name not in self.channels:
            channel = Channel(channel_name, context, unique_id)
            self.channels[channel_name] = channel

    def voicemailupdate(self, mailbox_id, new):
        self.handle_cti_stack('set', ('voicemails', 'updatestatus', mailbox_id))
        self.xod_status['voicemails'][mailbox_id]['new'] = new
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
            del self.channels[channel]

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

        aggregator = context.get('call_form_variable_aggregator')
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
            channel = aggregator.get(uid)['xivo'].get('channel')
            if not channel:
                continue

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
