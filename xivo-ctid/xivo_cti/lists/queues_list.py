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

import logging
from xivo_cti.cti_anylist import ContextAwareAnyList

logger = logging.getLogger('queuelist')


class QueuesList(ContextAwareAnyList):

    def __init__(self, innerdata):
        self._innerdata = innerdata
        ContextAwareAnyList.__init__(self, 'queues')

    def init_data(self):
        super(QueuesList, self).init_data()
        self._init_reverse_dictionary()

    def add(self, queue_id):
        super(QueuesList, self).add(queue_id)
        self._add_to_reverse_dictionary(queue_id)

    def delete(self, queue_id):
        self._remove_from_reverse_dictionary(queue_id)
        super(QueuesList, self).delete(queue_id)

    def _init_reverse_dictionary(self):
        self.reverse_index = {}
        for queue_id, queue in self.keeplist.iteritems():
            queue_name = queue['name']
            self.reverse_index[queue_name] = queue_id

    def _add_to_reverse_dictionary(self, queue_id):
        queue = self.keeplist[queue_id]
        queue_name = queue['name']
        self.reverse_index[queue_name] = queue_id

    def _remove_from_reverse_dictionary(self, queue_id):
        queue = self.keeplist[queue_id]
        queue_name = queue['name']
        del self.reverse_index[queue_name]

    def hasqueue(self, queuename):
        return queuename in self.reverse_index

    def idbyqueuename(self, queuename):
        if queuename in self.reverse_index:
            idx = self.reverse_index[queuename]
            if idx in self.keeplist:
                return idx

    def getcontext(self, queueid):
        return self.keeplist[queueid]['context']

    def get_queues(self):
        return self.keeplist.keys()
