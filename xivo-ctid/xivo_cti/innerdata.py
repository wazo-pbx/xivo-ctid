# -*- coding: utf-8 -*-

# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall'
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import copy
import hashlib
import logging
import os
import string
import time
import Queue
import cti_urllist
from xivo_cti import lists
from xivo_cti.lists import *
from xivo_cti.services import call_history_manager
from xivo_cti.directory import directory
from xivo_cti import cti_sheets
from xivo_cti import db_connection_manager
from xivo_dao.alchemy import dbconnection
from xivo_cti import cti_config
from xivo_cti.cti.commands.getlists.list_id import ListID
from xivo_cti.cti.commands.getlists.update_config import UpdateConfig
from xivo_cti.cti.commands.getlists.update_status import UpdateStatus
from xivo_cti.cti.commands.directory import Directory
from xivo_cti.cti.commands.availstate import Availstate
from xivo_cti.ami import ami_callback_handler
from xivo_cti.services.queue_service_manager import NotAQueueException
from xivo_cti.cti_config import Config
from xivo_cti.dao import userfeaturesdao

logger = logging.getLogger('innerdata')

ALPHANUMS = string.uppercase + string.lowercase + string.digits


class Safe(object):
    # matches between CTI lists and WEBI-given fields
    urlvars = {
        'users': 'urllist_users',
        'phones': 'urllist_lines',
        # 'devices' : 'urllist_devices',
        'agents': 'urllist_agents',
        'queues': 'urllist_queues',
        'groups': 'urllist_groups',
        'meetmes': 'urllist_meetmes',
        'voicemails': 'urllist_voicemails',
        'incalls': 'urllist_incalls',
        # 'outcalls' : 'urllist_outcalls',
        'contexts': 'urllist_contexts',
        # 'entities' : 'urllist_entities',
        'phonebooks': 'urllist_phonebook'
    }

    # defines the list of parameters that might be sent to xivo clients
    props_config = {
        'users': [
            'firstname',
            'lastname',
            'fullname',
            'mobilephonenumber',
            'profileclient',
            'enableclient',
            'agentid',
            'voicemailid',
            'enablerna',
            'enableunc',
            'enablebusy',
            'destrna',
            'destunc',
            'destbusy',
            'enablevoicemail',
            'enablednd',
            'enablexfer',
            'incallfilter',
            'linelist',
        ],
        'phones': [
            'context',
            'protocol',
            'number',
            'iduserfeatures',
            'rules_order',
            'identity',
            'initialized',
            'allowtransfer',
        ],
        'agents': [
            'context',
            'firstname',
            'lastname',
            'number',
        ],
        'queues': [
            'context',
            'name',
            'displayname',
            'number'
        ],
        'groups': [],
        'voicemails': [
            'context',
            'fullname',
            'mailbox',
            'email'
        ],
        'meetmes': [
            'context',
            'confno',
            'name',
            'admin_moderationmode',
            'pin_needed'
        ],
        'incalls': [
            'context',
            'exten',
            'destidentity',
            'action'
        ],
        'outcalls': [],
        'contexts': [],
        'phonebooks': [],
        'queuemembers': [
            'queue_name',
            'interface',
            'paused'
        ]
    }

    props_status = {'users': {'connection': None,
                              'availstate': 'disconnected'},
                    'phones': {'hintstatus': '4',
                               'channels': [],
                               'queues': [],
                               'groups': []},
                    'trunks': {'hintstatus': '-2',
                               'channels': [],
                               'queues': [],
                               'groups': []},
                    'agents': {'phonenumber': None, # static mode
                               'channel': None, # dynamic mode
                               'status': 'undefined', # statuses are AGENT_LOGGEDOFF, _ONCALL, _IDLE and '' (undefined)
                               'queues': [],
                               'groups': []},
                    'queues': {'agentmembers': [],
                               'phonemembers': [],
                               'incalls': []},
                    'groups': {'agentmembers': [],
                               'phonemembers': [],
                               'incalls': []},
                    'meetmes': {'pseudochan': None,
                                'channels': {},
                                'paused': False},
                    'voicemails': {'waiting': False,
                                   'old': 0,
                                   'new': 0},
                    'incalls': {},
                    'outcalls': {},
                    'contexts': {}}

    permission_kinds = ['regcommands', 'userstatus']

    def __init__(self, ctiserver, cnf=None):
        self._config = cti_config.Config.get_instance()
        self._ctiserver = ctiserver
        self.ipbxid = 'xivo'
        self.xod_config = {}
        self.xod_status = {}
        self.user_features_dao = None

        self.timeout_queue = Queue.Queue()

        self.channels = {}
        self.queuemembers = {}
        self.queuemembers_config = {}
        self.faxes = {}

        self.displays_mgr = directory.DisplaysMgr()
        self.contexts_mgr = directory.ContextsMgr()
        self.directories_mgr = directory.DirectoriesMgr()

        cdr_uri = self._config.getconfig('ipbx')['cdr_db_uri']
        dbconnection.add_connection(cdr_uri)
        self.call_history_mgr = call_history_manager.CallHistoryMgr.new_from_uri(cdr_uri)

        self.ctistack = []

        self.extenfeatures = {}

        if cnf and 'urllist_extenfeatures' in cnf:
            self.set_extenfeatures(cnf['urllist_extenfeatures'])

        for listname, urllistkey in self.urlvars.iteritems():
            try:
                cf = eval('lists.cti_%slist' % listname[:-1])
                cn = '%s%sList' % (listname[0].upper(), listname[1:-1])

                if cnf and urllistkey in cnf:
                    self.xod_config[listname] = getattr(cf, cn)(cnf[urllistkey])
                else:
                    logger.warning('no such key %s in configuration', urllistkey)
                    self.xod_config[listname] = getattr(cf, cn)()
                self.xod_config[listname].setcommandclass(self)
                self.xod_config[listname].setgetter('get_x_list')
                self.xod_status[listname] = {}
            except Exception:
                logger.exception("%s", listname)

    def register_cti_handlers(self):
        ListID.register_callback_params(self.handle_getlist_list_id, ['list_name', 'user_id'])
        UpdateConfig.register_callback_params(self.handle_getlist_update_config, ['user_id', 'list_name', 'item_id'])
        UpdateStatus.register_callback_params(self.handle_getlist_update_status, ['list_name', 'item_id'])
        Directory.register_callback_params(self.getcustomers, ['user_id', 'pattern', 'commandid'])
        Availstate.register_callback_params(self._ctiserver._user_service_manager.set_presence, ['user_id', 'availstate'])

    def register_ami_handlers(self):
        ami_handler = ami_callback_handler.AMICallbackHandler.get_instance()
        ami_handler.register_callback('AgentConnect', self.handle_agent_linked)
        ami_handler.register_callback('AgentComplete', self.handle_agent_unlinked)
        ami_handler.register_callback('Newstate', self.new_state)

    def _channel_extra_vars_agent_linked_unlinked(self, event):
        try:
            channel_name = event['Channel']
            if channel_name in self.channels:
                channel = self.channels[channel_name]
                proto, agent_number = event['Member'].split('/', 1)
                if proto == 'Agent':
                    data_type = 'agent'
                    data_id = self.xod_config['agents'].idbyagentnumber(agent_number)
                else:
                    data_type = 'user'
                    phone_id = self.zphones(proto, agent_number)
                    data_id = str(userfeaturesdao.find_by_line_id(phone_id))
                channel.set_extra_data('xivo', 'desttype', data_type)
                channel.set_extra_data('xivo', 'destid', data_id)
        except (AttributeError, LookupError):
            logger.warning('Failed to set agent channel variables for event: %s', event)

    def handle_agent_linked(self, event):
        # Will be called when joining a group/queue with an agent or user member
        self._channel_extra_vars_agent_linked_unlinked(event)
        try:
            channel = event['Channel']
            proto, agent_number = channel.split('/', 1)
            if proto == 'Agent' and channel in self.channels:
                self.sheetsend('agentlinked', event['Channel'])
        except KeyError:
            logger.warning('Could not split channel %s', channel)

    def handle_agent_unlinked(self, event):
        # Will be called when leaving a group/queue with an agent or user member
        self._channel_extra_vars_agent_linked_unlinked(event)
        if 'Channel' in event and event['Channel'] in self.channels:
            self.sheetsend('agentunlinked', event['Channel'])

    def handle_getlist_list_id(self, listname, user_id):
        if listname in self.xod_config or listname == 'queuemembers':
            if listname in self.xod_config:
                user_contexts = self.xod_config['users'].get_contexts(user_id)
                item_ids = self.xod_config[listname].list_ids_in_contexts(user_contexts)
            elif listname == 'queuemembers':
                item_ids = self.queuemembers_config.keys()
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

    def set_extenfeatures(self, urls):
        '''Retrieve and assign extenfeatures from a url list'''
        if not urls:
            self.extenfeatures = {}
            return
        extenfeatures = cti_urllist.UrlList(urls[0])
        extenfeatures.getlist(0, 0, False)
        self.extenfeatures = extenfeatures.jsonreply

    def fill_lines_into_users(self):
        user2phone = {}
        for idphone, v in self.xod_config['phones'].keeplist.iteritems():
            iduser = str(v.get('iduserfeatures'))
            if iduser not in user2phone:
                user2phone[iduser] = []
            if idphone not in user2phone[iduser]:
                user2phone[iduser].append(idphone)
        for iduser, v in self.xod_config['users'].keeplist.iteritems():
            v['linelist'] = user2phone.get(iduser, [])

    def config_from_external(self, listname, contents):
        function = contents.get('function')
        if function == 'listid':
            for k in contents.get('list'):
                self.xod_config[listname].keeplist[k] = {}
                self.xod_status[listname][k] = {}
        elif function == 'updateconfig':
            tid = contents.get('tid')
            self.xod_config[listname].keeplist[tid] = contents.get('config')
        elif function == 'updatestatus':
            tid = contents.get('tid')
            if self.xod_status[listname].get(tid) != contents.get('status'):
                self.xod_status[listname][tid] = contents.get('status')
                self._ctiserver.send_cti_event({'class': 'getlist',
                                                'listname': listname,
                                                'function': 'updatestatus',
                                                'tipbxid': self.ipbxid,
                                                'tid': tid,
                                                'status': self.xod_status[listname][tid]})

    def _initialize_item_status(self, listname, index):
        self.xod_status[listname][index] = {}
        if self.props_status.get(listname):
            self.xod_status[listname][index] = copy.deepcopy(self.props_status[listname])

    def _update_config_list_add(self, listname, deltas):
        changed = 'add' in deltas and len(deltas['add']) > 0
        for k in deltas.get('add', []):
            self._initialize_item_status(listname, k)

            message = {'class': 'getlist',
                       'listname': listname,
                       'function': 'addconfig',
                       'tipbxid': self.ipbxid,
                       'list': [k]}

            if not Config.get_instance().part_context():
                self._ctiserver.send_cti_event(message)
            else:
                if listname == 'users':
                    item_context = self.user_service_manager.get_context(k)
                else:
                    item_context = self.xod_config[listname].keeplist[k].get('context')
                connection_list = self._ctiserver.get_connected({'contexts': [item_context]})
                for connection in connection_list:
                    connection.append_msg(message)

        return changed

    def _update_config_list_del(self, listname, deltas):
        changed = 'del' in deltas and len(deltas['del']) > 0
        if changed:
            self._ctiserver.send_cti_event({'class': 'getlist',
                                            'listname': listname,
                                            'function': 'delconfig',
                                            'tipbxid': self.ipbxid,
                                            'list': deltas['del']})
        return changed

    def _update_config_list_change(self, listname, deltas):
        do_fill_lines = False
        for tid, v in deltas.get('change', {}).iteritems():
            if v:
                props = self.xod_config[listname].keeplist[tid]
                newc = {}
                for p in v:
                    if p in self.props_config.get(listname):
                        newc[p] = props[p]

                if newc:
                    message = {'class': 'getlist',
                               'listname': listname,
                               'function': 'updateconfig',
                               'tipbxid': self.ipbxid,
                               'tid': tid,
                               'config': newc}

                    self._ctiserver.send_cti_event(message)
                    do_fill_lines = True

        return do_fill_lines

    def update_config_list(self, listname, state, id):
        try:
            deltas = self.xod_config[listname].update()
            added = self._update_config_list_add(listname, deltas)
            deleted = self._update_config_list_del(listname, deltas)
            changed = self._update_config_list_change(listname, deltas)
            if listname in ['phones', 'users'] and (added or changed or deleted):
                self.fill_lines_into_users()
        except LookupError:
            logger.exception('update_config_list %s', listname)

    def update_config_list_all(self):
        for listname in self.urlvars:
            self.update_config_list(listname, None, None)

    def init_status(self):
        '''
        Initialize xod_status for lists that are not retrieved using web services
        '''
        self.xod_status['trunks'] = {}
        trunk_ids = self.trunk_features_dao.get_ids()
        for trunk_id in trunk_ids:
            self.xod_status['trunks'][trunk_id] = copy.deepcopy(self.props_status['trunks'])

    def get_x_list(self, xlist):
        lxlist = {}
        for xitem in xlist:
            try:
                if not xitem.get('commented'):
                    # XXX to work over once redmine#2169 will be solved
                    if 'id' in xitem:
                        key = str(xitem.get('id'))
                    elif 'contextnumbers' in xitem:
                        # For contexts
                        key = xitem['context']['name']
                    else:
                        # for voicemail case
                        key = str(xitem.get('uniqueid'))
                    lxlist[key] = xitem
                    # meetme : admin_moderationmode => moderated
                    # meetme : uniqueids and adminnum statuses
            except KeyError:
                logger.exception('(get_x_list : %s)', xitem)
        return lxlist

    def user_match(self, userid, tomatch):
        domatch = False

        # does the user fullfil the destination criteria ?
        if 'desttype' in tomatch and 'destid' in tomatch:
            dest_type, dest_id = tomatch['desttype'], tomatch['destid']
            if dest_type == 'user' and userid == dest_id:
                domatch = True
            elif dest_type == 'agent':
                user = self.xod_config['users'].keeplist[userid]
                domatch = user['agentid'] == dest_id
            elif dest_type == 'queue' and dest_id:
                domatch = self.queuemember_service_manager.is_queue_member(userid, dest_id)
            elif dest_type == 'group' and dest_id:
                domatch = self.queuemember_service_manager.is_group_member(userid, dest_id)
        else:
            # 'all' case
            domatch = True

        if domatch and 'profileids' in tomatch:
            user = self.user_features_dao.get(userid)
            if user.profileclient not in tomatch.get('profileids'):
                domatch = False

        if domatch and 'entities' in tomatch:
            pass

        if domatch and 'contexts' in tomatch:
            domatch = False
            context = self.user_service_manager.get_context(userid)
            if context in tomatch['contexts']:
                domatch = True

        return domatch

    def find_users_channels_with_peer(self, user_id):
        '''Find a user's channels that that are talking to another channel'''
        potential_channel_start = []
        main_line = self.xod_config['phones'].get_main_line(user_id)
        agent = self.xod_config['agents'].get_agent_by_user(user_id)
        if main_line:
            potential_channel_start.append('%s/%s' % (main_line['protocol'], main_line['name']))
        if agent:
            potential_channel_start.append('Agent/%s' % agent['number'])

        def channel_filter(channel_key):
            '''Check if a channel (SIP/1234-xxxx) matches our potential channels'''
            for channel_start in potential_channel_start:
                if (channel_key.lower().startswith(channel_start.lower())
                    and self.channels[channel_key].peerchannel
                    and not self.channels[channel_key].properties['holded']):
                    return True

        return filter(channel_filter, self.channels)

    def user_get_hashed_password(self, userid, sessionid):
        tohash = '%s:%s' % (sessionid,
                            self.user_features_dao.get(userid).passwdclient)
        sha1sum = hashlib.sha1(tohash).hexdigest()
        return sha1sum

    def user_get_userstatuskind(self, userid):
        profileclient = self.user_features_dao.get_profile(userid)
        zz = self._config.getconfig('profiles').get(profileclient)
        return zz.get('userstatus')

    def get_config(self, listname, item_id, limit=None, user_contexts=None):
        reply = {}
        if listname == 'queuemembers':
            if item_id in self.queuemembers_config:
                reply = self.queuemembers_config[item_id]
            else:
                reply = {}
            return reply
        item_config = self.xod_config[listname].get_item_in_contexts(item_id, user_contexts)
        if not isinstance(item_config, dict):
            logger.warning('get_config : problem with item_id %s in listname %s',
                           item_id, listname)
            return reply

        if limit:
            for k in limit:
                if k in self.props_config.get(listname, []):
                    reply[k] = item_config.get(k)
        else:
            for k in self.props_config.get(listname, []):
                reply[k] = item_config.get(k)
        return reply

    def get_status_channel(self, channel_id, limit=None):
        if channel_id in self.channels:
            return self.channels[channel_id].properties

    def get_status_queuemembers(self, queue_member_id, limit=None):
        return self.queuemembers.get(queue_member_id)

    def get_status(self, listname, item_id, limit=None):
        if listname == 'channels':
            return self.get_status_channel(item_id, limit)
        if listname == 'queuemembers':
            return self.get_status_queuemembers(item_id, limit)
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

        if limit:
            for k in limit:
                if k in self.props_status.get(listname, {}):
                    reply[k] = periddict.get(k)
        else:
            for k in self.props_status.get(listname, {}):
                reply[k] = periddict.get(k)

        return reply

    def new_state(self, event):
        channel = event['Channel']
        state = event['ChannelState']
        description = event['ChannelStateDesc']

        if channel in self.channels:
            self.channels[channel].update_state(state, description)

    def newchannel(self, channel_name, context, state, state_description, unique_id):
        if not channel_name:
            return
        if channel_name not in self.channels:
            channel = Channel(channel_name, context, unique_id)
            self.channels[channel_name] = channel
        self.handle_cti_stack('setforce', ('channels', 'updatestatus', channel_name))
        self.updaterelations(channel_name)
        self.channels[channel_name].update_state(state, state_description)
        self.handle_cti_stack('empty_stack')

    def meetmeupdate(self, confno, channel=None, opts={}):
        mid = self.xod_config['meetmes'].idbyroomnumber(confno)
        if mid is None:
            return None
        status = self.xod_status['meetmes'][mid]
        self.handle_cti_stack('set', ('meetmes', 'updatestatus', mid))
        if channel:
            if channel not in status['channels']:
                keys = ('isadmin', 'usernum', 'ismuted', 'isauthed')
                status['channels'][channel] = dict.fromkeys(keys)
            status['pseudochan'] = (opts.get('pseudochan')
                                    or status['pseudochan'])
            chan = status['channels'][channel]
            if 'admin' in opts:
                chan['isadmin'] = opts['admin']
            if 'muted' in opts:
                chan['ismuted'] = opts['muted']
            chan['usernum'] = opts.get('usernum') or chan['usernum']
            if 'authed' in opts:
                chan['isauthed'] = opts['authed']
            if 'leave' in opts:
                status['channels'].pop(channel)
            else:
                if channel in self.channels:
                    self.handle_cti_stack('set', ('channels', 'updatestatus', channel))
                    self.channels[channel].properties['talkingto_kind'] = '<meetme>'
                    self.channels[channel].properties['talkingto_id'] = mid
                    self.handle_cti_stack('empty_stack')
        elif opts and 'paused' in opts:
            # (pause)
            status['paused'] = opts['paused']
        else:
            # (end)
            status['pseudochan'] = None
            status['channels'] = {}
        self.handle_cti_stack('empty_stack')

    def agentlogin(self, agentnumber, channel):
        idx = self.xod_config['agents'].idbyagentnumber(agentnumber)
        self.handle_cti_stack('set', ('agents', 'updatestatus', idx))
        agstatus = self.xod_status['agents'].get(idx)
        if '@' in channel:
            # static agent mode
            agstatus['phonenumber'] = channel.split('@')[0]
        else:
            # dynamic agent mode
            agstatus['channel'] = channel
        agstatus['status'] = 'AGENT_IDLE'
        # define relations for agent:x : channel:y and phone:z
        self.handle_cti_stack('empty_stack')

    def agentlogout(self, agentnumber):
        idx = self.xod_config['agents'].idbyagentnumber(agentnumber)
        self.handle_cti_stack('set', ('agents', 'updatestatus', idx))
        agstatus = self.xod_status['agents'].get(idx)
        agstatus['status'] = 'AGENT_LOGGEDOFF'
        # define relations for agent:x : channel:y and phone:z
        self.handle_cti_stack('empty_stack')

    def agentstatus(self, agentnumber, status):
        idx = self.xod_config['agents'].idbyagentnumber(agentnumber)
        self.handle_cti_stack('set', ('agents', 'updatestatus', idx))
        agstatus = self.xod_status['agents'].get(idx)
        agstatus['status'] = status
        # define relations for agent:x : channel:y and phone:z
        self.handle_cti_stack('empty_stack')

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

    def _update_agent_member(self, location, props, queue_id, list_name):
        aid = self.xod_config['agents'].idbyagentnumber(location[6:])
        queue_member_id = None
        if aid:
            self.handle_cti_stack('set', ('agents', 'updatestatus', aid))
            queue_member_id = '%sa:%s-%s' % (list_name[0], queue_id, aid)
        # todo : group all this stuff, take care of relations
            if props:
                if aid not in self.xod_status[list_name][queue_id]['agentmembers']:
                    self.xod_status[list_name][queue_id]['agentmembers'].append(aid)
                if queue_id not in self.xod_status['agents'][aid][list_name]:
                    self.xod_status['agents'][aid][list_name].append(queue_id)
            else:
                if aid in self.xod_status[list_name][queue_id]['agentmembers']:
                    self.xod_status[list_name][queue_id]['agentmembers'].remove(aid)
                if queue_id in self.xod_status['agents'][aid][list_name]:
                    self.xod_status['agents'][aid][list_name].remove(queue_id)
        return queue_member_id

    def _update_phone_member(self, location, props, queue_id, list_name):
        queue_member_id = None
        termination = self.ast_channel_to_termination(location)
        pid = self.zphones(termination.get('protocol'), termination.get('name'))
        if pid:
            self.handle_cti_stack('set', ('phones', 'updatestatus', pid))
            queue_member_id = '%sp:%s-%s' % (list_name[0], queue_id, pid)
            if props:
                if pid not in self.xod_status[list_name][queue_id]['phonemembers']:
                    self.xod_status[list_name][queue_id]['phonemembers'].append(pid)
                if queue_id not in self.xod_status['phones'][pid][list_name]:
                    self.xod_status['phones'][pid][list_name].append(queue_id)
            else:
                if pid in self.xod_status[list_name][queue_id]['phonemembers']:
                    self.xod_status[list_name][queue_id]['phonemembers'].remove(pid)
                if queue_id in self.xod_status['phones'][pid][list_name]:
                    self.xod_status['phones'][pid][list_name].remove(queue_id)
        return queue_member_id

    def _update_queue_member(self, props, queue_member_id):
        if props:
            self.handle_cti_stack('set', ('queuemembers', 'updatestatus', queue_member_id))
            queue_member_status = self._extract_queue_member_status(props)
            self._update_queue_member_status(queue_member_id, queue_member_status)
        elif queue_member_id in self.queuemembers:
            self._remove_queue_member(queue_member_id)

    def queuememberupdate(self, name, location, props=None):
        if self.xod_config['queues'].hasqueue(name):
            list_name = 'queues'
        elif self.xod_config['groups'].hasqueue(name):
            list_name = 'groups'
        else:
            raise ValueError('%s is not a group or queue' % name)

        item_id = self.xod_config[list_name].idbyqueuename(name)

        # send a notification event if no new member
        self.handle_cti_stack('set', (list_name, 'updatestatus', item_id))
        if location.lower().startswith('agent/'):
            queue_member_id = self._update_agent_member(location, props, item_id, list_name)
        else:
            queue_member_id = self._update_phone_member(location, props, item_id, list_name)

        self._update_queue_member(props, queue_member_id)

        # send cti events in reverse order in order for the queuemember details to be received first
        self.handle_cti_stack('empty_stack')

    def _extract_queue_member_status(self, properties):
        if len(properties) == 6:
            (status, paused, membership, callstaken, penalty, lastcall) = properties
            return {'status': status,
                    'paused': paused,
                    'membership': membership,
                    'callstaken': callstaken,
                    'penalty': penalty,
                    'lastcall': lastcall}
        elif len(properties) == 1:
            (paused,) = properties
            return {'paused': paused}

    def _remove_queue_member(self, queue_member_id):
        del self.queuemembers[queue_member_id]
        self._ctiserver.send_cti_event({'class': 'getlist',
                                        'listname': 'queuemembers',
                                        'function': 'delconfig',
                                        'tipbxid': self.ipbxid,
                                        'list': [queue_member_id]})

    def _update_queue_member_status(self, queue_member_id, status):
        if queue_member_id not in self.queuemembers:
            self.queuemembers[queue_member_id] = {}
        for k, v in status.iteritems():
            self.queuemembers[queue_member_id][k] = v

    def update(self, channel):
        chanprops = self.channels.get(channel)
        relations = chanprops.relations
        for r in relations:
            if r.startswith('user:'):
                self.handle_cti_stack('setforce', ('users', 'updatestatus', r[5:]))
            elif r.startswith('phone:'):
                self.handle_cti_stack('setforce', ('phones', 'updatestatus', r[6:]))
        self.handle_cti_stack('setforce', ('channels', 'updatestatus', channel))
        self.handle_cti_stack('empty_stack')

    def statusbylist(self, listname, item_id):
        if listname == 'channels':
            if item_id and item_id in self.channels:
                return self.channels[item_id].properties
        elif listname == 'queuemembers':
            if item_id and item_id in self.queuemembers:
                return self.queuemembers.get(item_id)
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
            self._ctiserver.send_cti_event({'class': 'getlist',
                                            'listname': 'channels',
                                            'function': 'delconfig',
                                            'tipbxid': self.ipbxid,
                                            'list': [channel]})

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

    def updatehint(self, hint, status):
        termination = self.ast_channel_to_termination(hint)
        p = self.zphones(termination.get('protocol'), termination.get('name'))
        if p:
            oldstatus = self.xod_status['phones'][p]['hintstatus']
            self.xod_status['phones'][p]['hintstatus'] = status
            if status != oldstatus:
                self._ctiserver.send_cti_event({'class': 'getlist',
                                                'listname': 'phones',
                                                'function': 'updatestatus',
                                                'tipbxid': self.ipbxid,
                                                'tid': p,
                                                'status': {'hintstatus': status}})

    def updaterelations(self, channel):
        self.channels[channel].relations = []
        if channel.startswith('SIPPeer/'):
            return
        if channel.startswith('Parked/'):
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

    def masquerade(self, oldchannel, newchannel):
        try:
            oldrelations = self.channels[oldchannel].relations
            newrelations = self.channels[newchannel].relations

            oldchannelz = oldchannel + '<ZOMBIE>'
            self.channels[oldchannelz] = self.channels.pop(newchannel)
            self.channels[oldchannelz].channel = oldchannelz
            self.channels[newchannel] = self.channels.pop(oldchannel)
            self.channels[newchannel].channel = newchannel

            for r in oldrelations:
                if r.startswith('phone:'):
                    p = r[6:]
                    self.xod_status['phones'][p]['channels'].remove(oldchannel)
                    self.channels[newchannel].delrelation(r)
            self.channels[newchannel].relations = newrelations
            newfirstchannel = self.channels[newchannel].peerchannel
            if newfirstchannel:
                self.setpeerchannel(newfirstchannel, newchannel)
        except KeyError:
            logger.warning('Trying to do as masquerade on an unexistant channel')

    def usersummary_from_phoneid(self, phoneid):
        usersummary = {}
        if phoneid in self.xod_config['phones'].keeplist:
            phoneprops = self.xod_config['phones'].keeplist[phoneid]
            userid = str(phoneprops['iduserfeatures'])
            user = self.user_features_dao.get(userid)
            usersummary = {'phonenumber': phoneprops.get('number'),
                           'userid': userid,
                           'context': phoneprops.get('context'),
                           'fullname': user.fullname}
        return usersummary

    def setpeerchannel(self, channel, peerchannel):
        chanprops = self.channels.get(channel)
        chanprops.peerchannel = peerchannel
        chanprops.properties['talkingto_id'] = peerchannel
        if peerchannel and self.channels.get(peerchannel).relations:
            for k in self.channels.get(peerchannel).relations:
                if k.startswith('phone'):
                    usersummary = self.usersummary_from_phoneid(k[6:])
                    chanprops.properties['peerdisplay'] = '%s (%s)' % (usersummary.get('fullname'),
                                                                       usersummary.get('phonenumber'))

    def currentstatus(self):
        rep = []
        rep.append('* full status on %s' % time.asctime())
        rep.append('* channels')
        for k, v in self.channels.iteritems():
            rep.append('  * %s' % k)
            rep.append('    * relations : %s' % v.relations)
            if v.peerchannel:
                rep.append('    * peerchannel : %s' % v.peerchannel)
            rep.append('    * properties : %s' % v.properties)
        rep.append('* phones')
        for k, v in self.xod_status['phones'].iteritems():
            rep.append('  * %s :' % k)
            if v.get('hintstatus'):
                rep.append('    * hintstatus : %s' % v.get('hintstatus'))
            if v.get('channels'):
                rep.append('    * channels : %s' % v.get('channels'))
        rep.append('* agents')
        for k, v in self.xod_status['agents'].iteritems():
            rep.append('  * %s :' % k)
        rep.append('* queues')
        for k, v in self.xod_status['queues'].iteritems():
            rep.append('  * %s :' % k)
        rep.append('--------------')
        return rep

    def get_user_permissions(self, kind, userid):
        ret = {}
        if kind not in self.permission_kinds:
            return ret
        profileclient = self.user_features_dao.get_profile(userid)
        if profileclient:
            profilespecs = self._config.getconfig('profiles').get(profileclient)
            if profilespecs:
                kindid = profilespecs.get(kind)
                if kindid:
                    ret = self._config.getconfig(kind).get(kindid)
                else:
                    logger.warning('get_user_permissions %s %s : no kindid', kind, userid)
            else:
                logger.warning('get_user_permissions %s %s : no profilespecs', kind, userid)
        else:
            logger.warning('get_user_permissions %s %s : no profileclient', kind, userid)
        return ret

    # IPBX side

    def ast_channel_to_termination(self, channel):
        term = {}
        # special cases : AsyncGoto/IAX2/asteriskisdn-13622<ZOMBIE>
        # Parked/SIP, Parked/IAX2, SCCP, DAHDI, Parked/SCCP ...
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
            return self.trunk_features_dao.find_by_proto_name(protocol, name)
        except (LookupError, ValueError):
            return None

    def fill_user_ctilog(self, uri, userid, what, options='', callduration=None):
        request = "INSERT INTO ctilog (${columns}) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        columns = ('eventdate', 'loginclient', 'company', 'status',
                   'action', 'arguments', 'callduration')
        datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        user = self.user_features_dao.get(userid)
        userstatus = self.xod_status.get('users').get(userid).get('availstate')
        arguments = (datetime,
                     user.loginclient,
                     user.entityid,
                     userstatus,
                     what, options, callduration)

        with db_connection_manager.DbConnectionPool(uri) as connection:
            connection['cur'].query(request, columns, arguments)
            connection['conn'].commit()

    def sheetsend(self, where, channel, outdest=None):
        if 'sheets' not in self._config.getconfig():
            return
        bsheets = self._config.getconfig('sheets')
        self.sheetevents = bsheets.get('events')
        self.sheetdisplays = bsheets.get('displays')
        self.sheetoptions = bsheets.get('options')
        self.sheetconditions = bsheets.get('conditions')
        if where not in self.sheetevents:
            return

        if channel not in self.channels and not channel.startswith('special'):
            return

        for se in self.sheetevents[where]:
            display_id = se.get('display')
            condition_id = se.get('condition')
            option_id = se.get('option')

            if not self.sheetdisplays.get(display_id):
                continue

            channelprops = self.channels.get(channel)
            channelprops.set_extra_data('xivo', 'time', time.strftime('%H:%M:%S', time.localtime()))
            channelprops.set_extra_data('xivo', 'date', time.strftime('%Y-%m-%d', time.localtime()))
            channelprops.set_extra_data('xivo', 'where', where)
            channelprops.set_extra_data('xivo', 'channel', channel)
            channelprops.set_extra_data('xivo', 'context', channelprops.context)
            channelprops.set_extra_data('xivo', 'uniqueid', channelprops.unique_id)
            channelprops.set_extra_data('xivo', 'ipbxid', self.ipbxid)
            sheet = cti_sheets.Sheet(where, self.ipbxid, channel)
            sheet.setoptions(self.sheetoptions.get(option_id))
            sheet.setdisplays(self.sheetdisplays.get(display_id))
            sheet.setconditions(self.sheetconditions.get(condition_id))

            # 1. whom / userinfos : according to outdest or destlist to update in Channel structure
            #    + according to conditions
            #    final 'whom' description should be clearly written in order to send across 'any path'
            tomatch = sheet.checkdest(channelprops)
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

    # Timers/Synchro stuff - begin

    def checkqueue(self):
        ncount = 0
        while self.timeout_queue.qsize() > 0:
            ncount += 1
            received = self.timeout_queue.get()
            (toload,) = received
            action = toload.get('action')
            if action == 'fax':
                properties = toload.get('properties')
                step = properties.get('step')
                fileid = properties.get('fileid')
                removeme = self.faxes[fileid].step(step)
                if removeme:
                    params = self.faxes[fileid].getparams()
                    actionid = fileid
                    self._ctiserver.myami.execute_and_track(actionid, params)
                    del self.faxes[fileid]

            # other cases to handle : login, agentlogoff (would that still be true ?)
        return ncount

    def cb_timer(self, *args):
        try:
            self.timeout_queue.put(args)
            os.write(self._ctiserver.pipe_queued_threads[1], 'innerdata:%s\n' % self.ipbxid)
        except Exception:
            logger.exception('cb_timer %s', args)

    def update_directories(self):
        # This function must be called after a certain amount of initialization
        # went by in the _ctiserver object since some of the directories depends on
        # some information which is not available during this Safe __init__
        display_contents = self._config.getconfig('displays')
        self.displays_mgr.update(display_contents)

        directories_contents = self._config.getconfig('directories')
        self.directories_mgr.update(self._ctiserver, directories_contents)

        contexts_contents = self._config.getconfig('contexts')
        self.contexts_mgr.update(self.displays_mgr.displays,
                                 self.directories_mgr.directories,
                                 contexts_contents)

    # directory lookups entry points - START

    def getcustomers(self, user_id, pattern, commandid):
        try:
            context = self.user_service_manager.get_context(user_id)
            context_obj = self.contexts_mgr.contexts[context]
        except KeyError:
            logger.info('Directory lookup failed in context: %s', context)
            return 'warning', {'status': 'ko', 'reason': 'undefined_context'}
        else:
            headers, resultlist = context_obj.lookup_direct(pattern, contexts=[context])
            resultlist = list(set(resultlist))
            return 'message', {'class': 'directory',
                               'headers': headers,
                               'replyid': commandid,
                               'resultlist': resultlist,
                               'status': 'ok'}

    # directory lookups entry points - STOP


class Channel(object):

    extra_vars = {'xivo': ['agentnumber', 'calledidname', 'calledidnum',
                           'calleridname', 'calleridnum', 'calleridrdnis',
                           'calleridton', 'channel', 'context', 'date',
                           'destid', 'desttype', 'did', 'direction',
                           'directory', 'ipbxid', 'origin', 'queuename', 'time',
                           'uniqueid', 'userid', 'where'],
                  'dp': [],
                  'db': []}

    def __init__(self, channel, context, unique_id=None):
        self.channel = channel
        self.peerchannel = None
        self.context = context
        self.unique_id = unique_id
        # destlist to update along the incoming channel path, in order
        # to be ready when a sheet will be sent to the 'destination'

        self.properties = {
            'holded': False,
            'parked': False,
            'direction': None,
            'commstatus': 'ready',
            'timestamp': time.time(),
            'peerdisplay': None,
            'talkingto_kind': None,
            'talkingto_id': None,
            'state': 'Unknown',
        }
        self.relations = []
        self.extra_data = {}

    def setparking(self, exten, parkinglot):
        self.properties['peerdisplay'] = 'Parking (%s in %s)' % (exten, parkinglot)
        self.properties['parked'] = True
        self.properties['talkingto_kind'] = 'parking'
        self.properties['talkingto_id'] = '%s@%s' % (exten, parkinglot)

    def unsetparking(self):
        self.properties['peerdisplay'] = None
        self.properties['parked'] = False
        self.properties['talkingto_kind'] = None
        self.properties['talkingto_id'] = None

    def addrelation(self, relation):
        if relation not in self.relations:
            self.relations.append(relation)

    def delrelation(self, relation):
        if relation in self.relations:
            self.relations.remove(relation)

    def update_state(self, state, description):
        # values
        # 0 Down (creation time)
        # 5 Ringing
        # 6 Up
        self.state = state
        if description:
            self.properties['state'] = description

    # extra dialplan data that may be reachable from sheets

    def set_extra_data(self, family, varname, varvalue):
        if family not in self.extra_vars:
            return
        if family not in self.extra_data:
            self.extra_data[family] = {}
        if family == 'xivo':
            if varname in self.extra_vars.get(family):
                self.extra_data[family][varname] = varvalue
        else:
            self.extra_data[family][varname] = varvalue

    def has_extra_data(self, family, varname):
        return family in self.extra_data and varname in self.extra_data[family]


def split_channel(channel):
    protocol, end = channel.split('/', 1)
    if protocol.lower() in ['iax', 'sip', 'sccp', 'local']:
        name = '-'.join(end.split('-')[0:end.count('-')])
    else:
        protocol = 'custom'
        name = '/'.join(channel.split('/')[0:channel.count('/')])
    return protocol, name
