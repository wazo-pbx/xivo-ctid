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
# contracted with Avencall. See the LICENSE file at top of the source tree
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

import logging
from xivo_dao import group_dao
from xivo_dao.helpers import queuemember_formatter
from xivo_cti.tools.delta_computer import DictDelta
from xivo_dao import queue_features_dao
from xivo_cti.dao import userfeaturesdao

logger = logging.getLogger("QueueMemberServiceManager")


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
        delta = DictDelta(queuemember_formatted, {}, {})
        self.queuemember_notifier.queuemember_config_updated(delta)

    def remove_dynamic_queuemember(self, ami_event):
        queuemember_formatted = queuemember_formatter.QueueMemberFormatter.format_queuemember_from_ami_remove(ami_event)
        delta = DictDelta({}, {}, queuemember_formatted)
        self.queuemember_notifier.queuemember_config_updated(delta)

    def update_one_queuemember(self, ami_event):
        new_queuemembers = queuemember_formatter.QueueMemberFormatter.format_queuemember_from_ami_update(ami_event)
        old_queuemembers = self.innerdata_dao.get_queuemembers_config()
        delta = self.delta_computer.compute_delta_no_delete(new_queuemembers, old_queuemembers)
        self.queuemember_notifier.queuemember_config_updated(delta)

    def _get_queuemembers_to_request(self, delta):
        ret = []
        for queuemember in delta.add.itervalues():
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
        delta = DictDelta({}, queuemember_formatted, {})
        self.queuemember_notifier.queuemember_config_updated(delta)

    def dispach_command(self, command, member, queue, dopause=None):
        item, item2 = member.split(':', 1)
        server, agent_id = item2.split('/', 1)
        item, item2 = queue.split(':', 1)
        server, queue_id = item2.split('/', 1)

        if queue_id == 'all':
            queue_name = 'all'
        else:
            queue_name = queue_features_dao.queue_name(queue_id)

        if command in ['queuepause', 'queueunpause'] and dopause is not None:
            if queue_name == 'all':
                if command == 'queuepause':
                    self.agent_service_manager.queuepause_all(agent_id)
                else:
                    self.agent_service_manager.queueunpause_all(agent_id)
            else:
                if dopause:
                    self.agent_service_manager.queuepause(queue_name, agent_id)
                else:
                    self.agent_service_manager.queueunpause(queue_name, agent_id)
        elif command == 'queueadd':
            self.agent_service_manager.queueadd(queue_name, agent_id)
        elif command == 'queueremove':
            self.agent_service_manager.queueremove(queue_name, agent_id)

    def is_queue_member(self, user_id, queue_id):
        try:
            queue_name = queue_features_dao.get_queue_name(queue_id)
        except LookupError:
            return False

        lowered_keys = map(lambda x: x.lower(),
                           self.innerdata_dao.get_queuemembers_config().keys())

        try:
            chan = ('Agent/%s' % (userfeaturesdao.get_agent_number(user_id))).lower()
        except LookupError:
            pass  # User has no agent or it's a group
        else:
            key = '%s,%s' % (chan, queue_name)
            if key in lowered_keys:
                return True

        try:
            line_proto_name = userfeaturesdao.get_line_identity(user_id)
        except LookupError:
            pass  # This user has no line
        else:
            key = '%s,%s' % (line_proto_name.lower(), queue_name)
            if key in lowered_keys:
                return True

        return False

    def is_group_member(self, user_id, group_id):
        try:
            group_name = group_dao.get_name(group_id)
            line_proto_name = userfeaturesdao.get_line_identity(user_id)
        except KeyError:
            return False
        else:
            lowered_keys = map(lambda x: x.lower(),
                               self.innerdata_dao.get_queuemembers_config().keys())

            return '%s,%s' % (line_proto_name.lower(), group_name) in lowered_keys
