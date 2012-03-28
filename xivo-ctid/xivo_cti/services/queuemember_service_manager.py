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
        old_queuemembers = self.innerdata_dao.get_queuemembers_config()
        delta = self.delta_computer.compute_delta(new_queuemembers, old_queuemembers)
        self.queuemember_notifier.queuemember_config_updated(delta)

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
