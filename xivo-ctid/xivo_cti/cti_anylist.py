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

import time
import copy
import logging
from collections import defaultdict
from xivo_cti import cti_daolist
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.ioc.context import context as cti_context

logger = logging.getLogger('anylist')


class AnyList(object):

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
            'admin_moderationmode'
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
    props_status = {
        'users': {
            'connection': None,
            'availstate': 'disconnected'
        },
        'phones': {
            'hintstatus': '4',
            'channels': [],
            'queues': [],
            'groups': []
        },
        'trunks': {
            'hintstatus': '-2',
            'channels': [],
            'queues': [],
            'groups': []
        },
        'agents': {
            'phonenumber': None,
            'channel': None,
            'availability': AgentStatus.logged_out,
            'availability_since': time.time(),
            'on_call': False,
            'on_wrapup': False,
            'queues': [],
            'groups': []
        },
        'queues': {
            'agentmembers': [],
            'phonemembers': [],
        },
        'groups': {
            'agentmembers': [],
            'phonemembers': [],
        },
        'meetmes': {
            'pseudochan': None,
            'channels': {},
            'paused': False
        },
        'voicemails': {
            'waiting': False,
            'old': 0,
            'new': 0
        },
        'contexts': {},
        'phonebooks': {}
    }

    def __init__(self, listname):
        self.keeplist = {}
        self.listname = listname
        self.listname_obj = cti_daolist.DaoList(listname)
        self._ctiserver = self._innerdata._ctiserver
        self.ipbxid = self._innerdata.ipbxid

    def init_data(self):
        self.keeplist = self.listname_obj.get_list()

    def init_status(self):
        res = {}
        for list_id in self.keeplist.iterkeys():
            res[list_id] = copy.deepcopy(self.props_status[self.listname])
        return res

    def get_status(self):
        return copy.deepcopy(self.props_status[self.listname])

    def add(self, id):
        self.keeplist.update(self.listname_obj.get(id))
        self.add_notifier(id)

    def add_notifier(self, id):
        message = {'class': 'getlist',
                   'listname': self.listname,
                   'function': 'addconfig',
                   'tipbxid': self.ipbxid,
                   'list': [id]}

        if not cti_context.get('config').part_context():
            self._ctiserver.send_cti_event(message)
        else:
            if self.listname == 'users':
                item_context = self.get_contexts(id)
            else:
                item_context = [self.keeplist[id].get('context')]
            connection_list = self._ctiserver.get_connected({'contexts': item_context})
            for connection in connection_list:
                connection.append_msg(message)
        logger.debug('%s(%s) successfully added', self.listname, id)

    def edit(self, id):
        self.keeplist.update(self.listname_obj.get(id))
        self.edit_notifier(id)

    def edit_notifier(self, id):
        props = self.keeplist[id]
        newc = {}
        for p in props:
            if p in self.props_config.get(self.listname):
                newc[p] = props[p]
        if newc:
            message = {'class': 'getlist',
                       'listname': self.listname,
                       'function': 'updateconfig',
                       'tipbxid': self.ipbxid,
                       'tid': id,
                       'config': newc}
            self._ctiserver.send_cti_event(message)
        logger.debug('%s(%s) successfully updated', self.listname, id)

    def delete(self, id):
        del self.keeplist[id]
        self._ctiserver.send_cti_event({'class': 'getlist',
                                        'listname': self.listname,
                                        'function': 'delconfig',
                                        'tipbxid': self.ipbxid,
                                        'list': [id]})
        logger.debug('%s(%s) successfully deleted', self.listname, id)

    def get_item_config(self, item_id, user_contexts):
        reply = {}
        item_config = self.get_item_in_contexts(item_id, user_contexts)
        if not isinstance(item_config, dict):
            logger.warning('get_config : problem with item_id %s in listname %s',
                           item_id, self.listname)
            return reply

        for k in self.props_config.get(self.listname, []):
            reply[k] = item_config.get(k)

        return reply

    def get_item_status(self, periddict):
        reply = {}
        for k in self.props_status.get(self.listname, []):
            reply[k] = periddict.get(k)
        return reply

    def list_ids_in_contexts(self, contexts):
        return self.keeplist.keys()

    def get_item_in_contexts(self, item_id, contexts):
        return self.keeplist.get(item_id)


class ContextAwareAnyList(AnyList):

    def __init__(self, listname):
        AnyList.__init__(self, listname)
        self._item_ids_by_context = defaultdict(list)

    def init_data(self):
        AnyList.init_data(self)
        self._init_by_context_reverse_dict()

    def add(self, item_id):
        super(ContextAwareAnyList, self).add(item_id)
        self._add_to_by_context_dict(item_id)

    def delete(self, item_id):
        self._remove_from_by_context_dict(item_id)
        super(ContextAwareAnyList, self).delete(item_id)

    def _init_by_context_reverse_dict(self):
        item_ids_by_context = self._item_ids_by_context
        item_ids_by_context.clear()
        for item_id, item in self.keeplist.iteritems():
            context = item['context']
            item_ids_by_context[context].append(item_id)

    def _add_to_by_context_dict(self, item_id):
        item_context = self.keeplist[item_id]['context']
        item_ids = self._item_ids_by_context[item_context]
        if item_id not in item_ids:
            item_ids.append(item_id)

    def _remove_from_by_context_dict(self, item_id):
        item_context = self.keeplist[item_id]['context']
        item_ids = self._item_ids_by_context[item_context]
        item_ids.remove(item_id)
        if not item_ids:
            del self._item_ids_by_context[item_context]

    def list_ids_in_contexts(self, contexts):
        if not cti_context.get('config').part_context():
            return self.keeplist.keys()
        elif not contexts:
            return []
        elif len(contexts) == 1:
            return self._item_ids_by_context.get(contexts[0], [])
        else:
            item_ids = set()
            for context in contexts:
                item_ids.update(self._item_ids_by_context.get(context, []))
            return list(item_ids)

    def get_item_in_contexts(self, item_id, contexts):
        try:
            item = self.keeplist[item_id]
        except KeyError:
            return None
        else:
            if not cti_context.get('config').part_context():
                return item
            elif not contexts:
                return None
            else:
                if item['context'] in contexts:
                    return item
                return None
