# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
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

import logging
from xivo_cti.cti_anylist import ContextAwareAnyList

logger = logging.getLogger('queuelist')


class QueueList(ContextAwareAnyList):

    queuelocationprops = ['Paused', 'Status', 'Membership', 'Penalty',
                          'LastCall', 'CallsTaken', 'Xivo-QueueMember-StateTime']

    def __init__(self, newurls=[], misc=None):
        self.anylist_properties = {'name': 'queues',
                                    'urloptions': (1, 5, True)}
        ContextAwareAnyList.__init__(self, newurls)

    def update(self):
        ret = ContextAwareAnyList.update(self)
        self.reverse_index = {}
        for idx, ag in self.keeplist.iteritems():
            if ag['name'] not in self.reverse_index:
                self.reverse_index[ag['name']] = idx
            else:
                logger.warning('2 queues have the same name')
        return ret

    def hasqueue(self, queuename):
        return queuename in self.reverse_index

    def idbyqueuename(self, queuename):
        if queuename in self.reverse_index:
            idx = self.reverse_index[queuename]
            if idx in self.keeplist:
                return idx

    def getcontext(self, queueid):
        return self.keeplist[queueid]['context']

    def queueentry_rename(self, queueid, oldchan, newchan):
        if queueid in self.keeplist:
            if oldchan in self.keeplist[queueid]['channels']:
                self.keeplist[queueid]['channels'][newchan] = self.keeplist[queueid]['channels'][oldchan]
                del self.keeplist[queueid]['channels'][oldchan]
            else:
                logger.warning('queueentry_rename : channel %s is not in queueid %s',
                               oldchan, queueid)
        else:
            logger.warning('queueentry_rename : no such queueid %s', queueid)

    def queueentry_update(self, queueid, channel, position, entrytime, calleridnum, calleridname):
        if queueid in self.keeplist:
            self.keeplist[queueid]['channels'][channel] = {'position': position,
                                                           'entrytime': entrytime,
                                                           'calleridnum': calleridnum,
                                                           'calleridname': calleridname}

    def queueentry_remove(self, queueid, channel):
        if queueid in self.keeplist:
            if channel in self.keeplist[queueid]['channels']:
                del self.keeplist[queueid]['channels'][channel]
            else:
                logger.warning('queueentry_remove : channel %s is not in queueid %s',
                               channel, queueid)
        else:
            logger.warning('queueentry_remove : no such queueid %s', queueid)

    def queuememberremove(self, queueid, location):
        changed = False
        if queueid in self.keeplist:
            if location in self.keeplist[queueid]['agents_in_queue']:
                del self.keeplist[queueid]['agents_in_queue'][location]
                changed = True
        else:
            logger.warning('queuememberremove : no such queueid %s', queueid)
        return changed

    def get_queues(self):
        return self.keeplist.keys()

    def get_all_queues(self):
        return self.keeplist
