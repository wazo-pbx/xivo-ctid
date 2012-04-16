# -*- coding: utf-8 -*-

# XiVO CTI Server
# Copyright (C) 2009-2012  Avencall
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

from xivo_cti.dao.helpers import queuemember_formatter
from xivo_cti.tools.delta_computer import DictDelta

class QueueMemberServiceManager(object):

    def update_config(self):
        new_queuemembers = self.queuemember_dao.get_queuemembers()
        old_queuemembers = self.innerdata_dao.get_queuemembers_static()
        delta = self.delta_computer.compute_delta(new_queuemembers, old_queuemembers)
        queuemembers_request = self._get_queuemembers_to_request(delta)
        delta_remove_only = self._get_queuemembers_to_remove(delta)
        self.queuemember_notifier.request_queuemembers_to_ami(queuemembers_request)
        self.queuemember_notifier.queuemember_config_updated(delta_remove_only)

    def add_dynamic_queuemember(self, ami_event):
        queuemember_formatted = queuemember_formatter.QueueMemberFormatter.format_queuemember_from_ami_add(ami_event)
        delta = DictDelta(queuemember_formatted, {}, [])
        self.queuemember_notifier.queuemember_config_updated(delta)

    def remove_dynamic_queuemember(self, ami_event):
        queuemember_formatted = queuemember_formatter.QueueMemberFormatter.format_queuemember_from_ami_remove(ami_event)
        delta = DictDelta({}, {}, queuemember_formatted.keys())
        self.queuemember_notifier.queuemember_config_updated(delta)

    def update_one_queuemember(self, ami_event):
        new_queuemembers = queuemember_formatter.QueueMemberFormatter.format_queuemember_from_ami_update(ami_event)
        old_queuemembers = self.innerdata_dao.get_queuemembers_config()
        delta = self.delta_computer.compute_delta_no_delete(new_queuemembers, old_queuemembers)
        self.queuemember_notifier.queuemember_config_updated(delta)

    def _get_queuemembers_to_request(self, delta):
        ret = []
        for queuemember in delta.add.values():
            ret.append((queuemember['interface'], queuemember['queue_name']))
        for queuemember in delta.change:
            queuemember_local = self.innerdata_dao.get_queuemember(queuemember)
            ret.append((queuemember_local['interface'], queuemember_local['queue_name']))
        ret.sort()
        return ret

    def _get_queuemembers_to_remove(self, delta):
        return DictDelta({}, {}, delta.delete)

    def toggle_pause(self, ami_event):
        queuemember_formatted = queuemember_formatter.QueueMemberFormatter.format_queuemember_from_ami_pause(ami_event)
        delta = DictDelta({}, queuemember_formatted, [])
        self.queuemember_notifier.queuemember_config_updated(delta)

    def whenmember(self, innerdata, command, dopause, listname, k, member):
        memberlist = []
        midx = '%s%s:%s-%s' % (listname[0], member.get('type')[0], k, member.get('id'))
        membership = innerdata.queuemembers.get(midx).get('membership')
        paused = innerdata.queuemembers.get(midx).get('paused')
        doit = False
        if command == 'remove' and membership != 'static':
            doit = True
        if command == 'pause':
            if dopause == 'true' and paused == '0':
                doit = True
            if dopause == 'false' and paused == '1':
                doit = True
        if doit:
            memberlist.append(member)
        return memberlist

    def defmemberlist(self, innerdata, command, dopause, listname, k, member):
        memberlist = []
        if member.get('type') in ['phone', 'agent']:
            membersname = member.get('type') + 'members'
            lname = member.get('type') + 's'
            any_members = innerdata.xod_status.get(listname).get(k).get(membersname)
            if member.get('id') in innerdata.xod_config.get(lname).keeplist:
                if command == 'add':
                    if member.get('id') not in any_members:
                        memberlist = [member]
                else:
                    if member.get('id') in any_members:
                        memberlist = self.whenmember(innerdata, command, dopause, listname, k, member)
            elif member.get('id') == 'all':
                if command != 'add':
                    for any_id in any_members:
                        member = {'type': member.get('type'),
                                  'id': any_id}
                        memberlist = self.whenmember(innerdata, command, dopause, listname, k, member)
        return memberlist

    def makeinterfaces(self, innerdata, memberlist):
        interfaces = []
        for member in memberlist:
            interface = None
            if member.get('type') == 'phone':
                memberstruct = innerdata.xod_config.get('phones').keeplist.get(member.get('id'))
                interface = '%s/%s' % (memberstruct.get('protocol'), memberstruct.get('name'))
            elif member.get('type') == 'agent':
                memberstruct = innerdata.xod_config.get('agents').keeplist.get(member.get('id'))
                interface = 'Agent/%s' % memberstruct.get('number')

            if interface and interface not in interfaces:
                interfaces.append(interface)
        return interfaces
    
    def queue_generic(self, innerdata, command, queue, member, dopause=None):
        listname = None
        if queue.get('type') == 'queue':
            listname = 'queues'
        elif queue.get('type') == 'group':
            listname = 'groups'

        queuenames = []
        interfaces = []

        if listname:
            if queue.get('id') in innerdata.xod_config.get(listname).keeplist:
                lst = self.defmemberlist(innerdata, command, dopause, listname, queue.get('id'), member)
                if lst:
                    interfaces = self.makeinterfaces(innerdata, lst)
                    queuestruct = innerdata.xod_config.get(listname).keeplist.get(queue.get('id'))
                    queuename = queuestruct.get('name')
                    if queuename not in queuenames:
                        queuenames.append(queuename)
            elif queue.get('id') == 'all':
                for k, queuestruct in innerdata.xod_config.get(listname).keeplist.iteritems():
                    lst = self.defmemberlist(innerdata, command, dopause, listname, k, member)
                    if lst:
                        interfaces = self.makeinterfaces(innerdata, lst)
                        queuename = queuestruct.get('name')
                        if queuename not in queuenames:
                            queuenames.append(queuename)
        reps = []
        amicommand = 'queue%s' % command
        for queuename in queuenames:
            for interface in interfaces:
                if command == 'remove':
                    amiargs = (queuename, interface)
                elif command == 'add':
                    amiargs = (queuename, interface, dopause)
                elif command == 'pause':
                    amiargs = (queuename, interface, dopause)
                rep = {'amicommand': amicommand,
                       'amiargs': amiargs}
                reps.append(rep)
        return reps
