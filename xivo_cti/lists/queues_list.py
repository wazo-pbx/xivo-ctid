# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti_anylist import ContextAwareAnyList


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
        self.queues_by_name = dict((queue['name'], queue) for queue in self.keeplist.itervalues())

    def _add_to_reverse_dictionary(self, queue_id):
        queue = self.keeplist[queue_id]
        queue_name = queue['name']
        self.queues_by_name[queue_name] = queue

    def _remove_from_reverse_dictionary(self, queue_id):
        queue = self.keeplist[queue_id]
        queue_name = queue['name']
        del self.queues_by_name[queue_name]
