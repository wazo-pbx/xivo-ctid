#!/usr/bin/python
# vim: set fileencoding=utf-8 :

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

import time
from xivo_cti.services.queue_service_manager import NotAQueueException


class QueueMemberServiceNotifier(object):

    _instance = None

    def __init__(self):
        self._callbacks = list()

    def subscribe(self, function):
        self._callbacks.append(function)

    def queuemember_config_updated(self, delta):
        self.innerdata_dao.apply_queuemember_delta(delta)
        for event in self._prepare_queuemember_config_updated(delta):
            self.send_cti_event(event)
        for callback in self._callbacks:
            callback(delta)

    def _prepare_queuemember_config_updated(self, delta):
        return_template = {'class': 'getlist',
                           'listname': 'queuemembers',
                           'tipbxid': self.ipbx_id
                           }
        ret = []
        if delta.add:
            event = dict(return_template)
            add_list = delta.add.keys()
            update = {'function': 'addconfig',
                      'list': add_list,
                      }
            event.update(update)
            ret.append(event)
            for queuemember in delta.add.values():
                try:
                    queue_id = self.innerdata_dao.get_queue_id(queuemember['queue_name'])
                    self.queue_statistics_producer.on_agent_added(queue_id, queuemember['interface'])
                except NotAQueueException:
                    pass
        if delta.change:
            for queuemember_id in delta.change:
                event = dict(return_template)
                update = {'function': 'updateconfig',
                          'config': delta.change[queuemember_id],
                          'tid': queuemember_id}
                event.update(update)
                ret.append(event)
        if delta.delete:
            event = dict(return_template)
            del_list = delta.delete.keys()
            update = {'function': 'delconfig',
                      'list': del_list}
            event.update(update)
            ret.append(event)
            for queuemember in delta.delete.values():
                try:
                    queue_id = self.innerdata_dao.get_queue_id(queuemember['queue_name'])
                    self.queue_statistics_producer.on_agent_removed(queue_id, queuemember['interface'])
                except NotAQueueException:
                    pass
        return ret

    def request_queuemembers_to_ami(self, queuemembers_list):
        for (member, queue) in queuemembers_list:
            actionid = 'request_queuemember-%s-%s-%s' % (member,
                                                         queue,
                                                         time.time())
            params = {'mode': 'request_queuemember',
                      'amicommand': 'sendcommand',
                      'amiargs': ('queuestatus',
                                  [('Member', member),
                                   ('Queue', queue)])}
            self.interface_ami.execute_and_track(actionid, params)

    @classmethod
    def get_instance(cls):
        if cls._instance == None:
            cls._instance = cls()
        return cls._instance
