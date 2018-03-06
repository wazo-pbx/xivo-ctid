# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_utils import session_scope
from xivo_dao import queue_dao


class QueueEntryEncoder(object):

    MSG_TEMPLATE = {'class': 'queueentryupdate',
                    'state': None}

    QUEUE_ENTRY_TEMPLACE = {'position': None,
                            'name': None,
                            'number': None,
                            'join_time': None}

    STATE_TEMPLATE = {'queue_name': None,
                      'queue_id': None,
                      'entries': []}

    def encode(self, queue_name, entries):
        msg = dict(self.MSG_TEMPLATE)
        entry_list = self._build_entry_list(entries)
        msg['state'] = self._build_state(queue_name, entry_list)
        return msg

    def _encode_queue_entry(self, queue_entry):
        result = dict(self.QUEUE_ENTRY_TEMPLACE)

        result['position'] = queue_entry.position
        result['name'] = queue_entry.name
        result['number'] = queue_entry.number
        result['join_time'] = queue_entry.join_time
        result['uniqueid'] = queue_entry.unique_id

        return result

    def _build_entry_list(self, queue_entries):
        result = [self._encode_queue_entry(queue_entry)
                  for queue_entry in queue_entries.itervalues()]

        return sorted(result, key=lambda entry: entry['position'])

    def _build_state(self, queue_name, entry_list):
        state = dict(self.STATE_TEMPLATE)

        with session_scope():
            state['queue_name'] = queue_name
            state['queue_id'] = queue_dao.id_from_name(queue_name)
            state['entries'] = entry_list

        return state
