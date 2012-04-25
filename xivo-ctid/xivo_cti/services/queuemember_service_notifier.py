#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2011  Avencall
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
import logging

class QueueMemberServiceNotifier(object):

    def queuemember_config_updated(self, delta):
        self.innerdata_dao.apply_queuemember_delta(delta)
        for event in self._prepare_queuemember_config_updated(delta):
            self.events_cti.put(event)

    def _prepare_queuemember_config_updated(self, delta):
        return_template = {'class': 'getlist',
                           'listname': 'queuemembers',
                           'tipbxid': self.ipbx_id
                           }
        ret = []
        if delta.add:
            event = dict(return_template)
            add_list = delta.add.keys()
            add_list.sort()
            update = {'function': 'addconfig',
                      'list': add_list,
                      }
            event.update(update)
            ret.append(event)
            for queuemember in delta.add.values():
                self.queue_statistics_producer.on_agent_added(queuemember['queue_name'], queuemember['interface'])
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
            del_list = delta.delete
            del_list.sort()
            update = {'function': 'delconfig',
                    'list': del_list }
            event.update(update)
            ret.append(event)
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
