# XiVO CTI Server

#Copyright (C) 2007-2011  Avencall
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

import logging
import time
from xivo_cti.cti_anylist import ContextAwareAnyList

logger = logging.getLogger('agentlist')


class AgentList(ContextAwareAnyList):

    queuelocationprops = ['Paused', 'Status', 'Membership', 'Penalty', 'LastCall', 'CallsTaken',
                          'Xivo-QueueMember-StateTime']

    def __init__(self, newurls=[], useless=None):
        self.anylist_properties = {'name': 'agents',
                                   'urloptions': (1, 4, True)}
        ContextAwareAnyList.__init__(self, newurls)

    def update(self):
        ret = ContextAwareAnyList.update(self)
        self.reverse_index = {}
        for idx, ag in self.keeplist.iteritems():
            if ag['number'] not in self.reverse_index:
                self.reverse_index[ag['number']] = idx
            else:
                logger.warning('2 agents have the same number')
        return ret

    def queuememberupdate(self, queuename, queueorgroup, agentnumber, event):
        changed = False
        qorg = '%s_by_agent' % queueorgroup
        if agentnumber in self.reverse_index:
            idx = self.reverse_index[agentnumber]
            if idx in self.keeplist:
                if queuename not in self.keeplist[idx][qorg]:
                    self.keeplist[idx][qorg][queuename] = {}
                    changed = True
                thisagentqueueprops = self.keeplist[idx][qorg][queuename]
                for prop in self.queuelocationprops:
                    if prop in event:
                        if prop in thisagentqueueprops:
                            if thisagentqueueprops[prop] != event.get(prop):
                                thisagentqueueprops[prop] = event.get(prop)
                                changed = True
                        else:
                            thisagentqueueprops[prop] = event.get(prop)
                            changed = True
                if 'Xivo-QueueMember-StateTime' not in thisagentqueueprops:
                    thisagentqueueprops['Xivo-QueueMember-StateTime'] = time.time()
                    changed = True
        return changed

    def queuememberadded(self, queuename, queueorgroup, agentnumber, event):
        qorg = '%s_by_agent' % queueorgroup
        if agentnumber in self.reverse_index:
            idx = self.reverse_index[agentnumber]
            if idx in self.keeplist:
                if queuename not in self.keeplist[idx][qorg]:
                    self.keeplist[idx][qorg][queuename] = {}
                    for prop in self.queuelocationprops:
                        if prop in event:
                            self.keeplist[idx][qorg][queuename][prop] = event.get(prop)

    def queuememberremoved(self, queuename, queueorgroup, agentnumber, event):
        qorg = '%s_by_agent' % queueorgroup
        if agentnumber in self.reverse_index:
            idx = self.reverse_index[agentnumber]
            if idx in self.keeplist:
                if queuename in self.keeplist[idx][qorg]:
                    del self.keeplist[idx][qorg][queuename]

    def idbyagentnumber(self, agentnumber):
        idx = self.reverse_index.get(agentnumber)
        if idx in self.keeplist:
            return idx

    def get_agent_by_user(self, user_id):
        user = self.commandclass.xod_config['users'].keeplist[str(user_id)]
        return self.keeplist.get(user['agentid'])
