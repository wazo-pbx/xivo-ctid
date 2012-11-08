# -*- coding: utf-8 -*-

# Copyright (C) 2007-2012  Avencall

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


class QueueMemberDAO(object):
    def __init__(self, innerdata):
        self.innerdata = innerdata

    def get_paused_count_for_agent(self, agent_interface):
        queue_members = self.innerdata.xod_config['queuemembers'].keeplist
        paused_count = 0
        for queue_member in queue_members.itervalues():
            if queue_member['interface'] == agent_interface:
                if queue_member['paused'] is True:
                    paused_count += 1
        return paused_count

    def get_queue_count_for_agent(self, agent_interface):
        queue_members = self.innerdata.xod_config['queuemembers'].keeplist
        queue_count = 0
        for queue_member in queue_members.itervalues():
            if queue_member['interface'] == agent_interface:
                queue_count += 1
        return queue_count
